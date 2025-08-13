#!/usr/bin/env python3
"""
CPP to Java Equivalence Scorer

This script compares C++ field names with Java field names and calculates
the match percentage as Java fields matched divided by total C++ fields. It considers
field names equivalent if they match at least 80% after normalizing for case,
underscores, and special characters. Results: "excellent" (≥80%), "possible" (≥50%), 
or "no-match" (<50%) based on Java fields matched relative to total C++ fields.

Usage:
    python3 cpp_java_equivalence_scorer.py <cpp_file> <java_file>

Examples:
    - report_version (C++) matches _ReportVersion (Java) - equivalent
    - Both normalized to "reportversion" for comparison
"""

import sys
import json
import argparse
import re
from difflib import SequenceMatcher

try:
    from extract_variables import extract_variables_with_parent
    from extract_java_fields import extract_java_fields
except ImportError as e:
    print(f"Error: Missing required dependencies. Please activate virtual environment.", file=sys.stderr)
    print(f"Make sure tree_sitter_cpp and tree_sitter_java are installed.", file=sys.stderr)
    print(f"Original error: {e}", file=sys.stderr)
    sys.exit(1)


def normalize_field_name(name: str) -> str:
    """
    Normalize field name by:
    1. Converting to lowercase
    2. Removing underscores, dots, and other special characters
    3. Keeping only alphanumeric characters
    
    Args:
        name: The field name to normalize
        
    Returns:
        Normalized field name
    """
    # Remove all non-alphanumeric characters and convert to lowercase
    normalized = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
    return normalized


def calculate_similarity(cpp_name: str, java_name: str) -> float:
    """
    Calculate similarity between two field names using sequence matching.
    
    Args:
        cpp_name: C++ field name
        java_name: Java field name
        
    Returns:
        Similarity score as a percentage (0-100)
    """
    norm_cpp = normalize_field_name(cpp_name)
    norm_java = normalize_field_name(java_name)
    
    if not norm_cpp or not norm_java:
        return 0.0
    
    # Use SequenceMatcher to calculate similarity
    matcher = SequenceMatcher(None, norm_cpp, norm_java)
    similarity = matcher.ratio() * 100
    
    return similarity


def find_matches(cpp_fields: list, java_fields: list, threshold: float = 80.0) -> list:
    """
    Find potential matches between C++ and Java fields.
    
    Args:
        cpp_fields: List of C++ field dictionaries
        java_fields: List of Java field dictionaries
        threshold: Minimum similarity threshold (default: 80%)
        
    Returns:
        List of match dictionaries with scores
    """
    matches = []
    
    for cpp_field in cpp_fields:
        cpp_name = cpp_field['name']
        best_matches = []
        
        for java_field in java_fields:
            java_name = java_field['name']
            similarity = calculate_similarity(cpp_name, java_name)
            
            if similarity >= threshold:
                match = {
                    'cpp_field': cpp_field,
                    'java_field': java_field,
                    'similarity_score': round(similarity, 2),
                    'normalized_cpp': normalize_field_name(cpp_name),
                    'normalized_java': normalize_field_name(java_name)
                }
                best_matches.append(match)
        
        # Sort by similarity score (highest first)
        best_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        matches.extend(best_matches)
    
    return matches


def load_cpp_fields(cpp_file: str) -> list:
    """Load and extract C++ fields from file."""
    try:
        result = extract_variables_with_parent(cpp_file)
        if isinstance(result, dict) and 'variables' in result:
            return result['variables']
        else:
            return []
    except Exception as e:
        print(f"Error processing C++ file '{cpp_file}': {e}", file=sys.stderr)
        return []


def load_java_fields(java_file: str) -> list:
    """Load and extract Java fields from file."""
    try:
        with open(java_file, 'r', encoding='utf-8') as f:
            code = f.read()
        fields = extract_java_fields(code)
        # Filter out Java-specific field names that won't be available in C++
        ignored_fields = {
            'CODEGEN_VERSION',
            'TYPE_SIGNATURE', 
            'FAST_DEFAULT_FIELD_VALIDATION_MESSAGE',
            'FIELDQUALIFIER'
        }
        filtered_fields = [field for field in fields if field['name'] not in ignored_fields]
        return filtered_fields
    except Exception as e:
        print(f"Error processing Java file '{java_file}': {e}", file=sys.stderr)
        return []


def getMatchedResults(cpp_file: str, java_file: str, threshold: float = 80.0) -> dict:
    """
    Load C++ and Java fields, calculate matches and return comprehensive results.
    
    Args:
        cpp_file: Path to the C++ file
        java_file: Path to the Java file
        threshold: Minimum similarity threshold (default: 80%)
        
    Returns:
        Dictionary containing match results and statistics
    """
    # Load fields from both files
    cpp_fields = load_cpp_fields(cpp_file)
    java_fields = load_java_fields(java_file)
    
    if not cpp_fields or not java_fields:
        return {
            "cpp_file": cpp_file,
            "java_file": java_file,
            "threshold": threshold,
            "cpp_fields_count": len(cpp_fields) if cpp_fields else 0,
            "java_fields_count": len(java_fields) if java_fields else 0,
            "matches_found": 0,
            "cpp_fields_matched": 0,
            "java_fields_matched": 0,
            "match_percentage": 0.0,
            "final_result": "no-match",
            "matches": []
        }
    
    # Find matches
    matches = find_matches(cpp_fields, java_fields, threshold)
    
    # Calculate overall match statistics
    cpp_fields_with_matches = len(set(match['cpp_field']['name'] for match in matches))
    java_fields_with_matches = len(set(match['java_field']['name'] for match in matches))
    
    # Match percentage as Java fields matched / C++ fields total
    match_percentage = (java_fields_with_matches / len(cpp_fields)) * 100 if cpp_fields else 0
    
    # Determine final result based on match percentage
    has_significant_matches = len(matches) > 0
    if has_significant_matches and match_percentage >= 80:
        final_result = "excellent"
    elif has_significant_matches and match_percentage >= 50:
        final_result = "possible"
    else:
        final_result = "no-match"
    
    return {
        "cpp_file": cpp_file,
        "java_file": java_file,
        "threshold": threshold,
        "cpp_fields_count": len(cpp_fields),
        "java_fields_count": len(java_fields),
        "matches_found": len(matches),
        "cpp_fields_matched": cpp_fields_with_matches,
        "java_fields_matched": java_fields_with_matches,
        "match_percentage": round(match_percentage, 2),
        "final_result": final_result,
        "matches": matches
    }


def main():
    parser = argparse.ArgumentParser(
        description="Score equivalence between C++ and Java field names",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cpp_java_equivalence_scorer.py file.h Class.java
  python3 cpp_java_equivalence_scorer.py file.h Class.java --threshold 85
  python3 cpp_java_equivalence_scorer.py file.h Class.java --output matches.json
        """
    )
    parser.add_argument("cpp_file", help="Path to the C++ header file")
    parser.add_argument("java_file", help="Path to the Java file")
    parser.add_argument("--threshold", "-t", type=float, default=80.0,
                       help="Minimum similarity threshold (default: 80.0)")
    parser.add_argument("--output", "-o", help="Output JSON file (default: stdout)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed comparison information")
    
    args = parser.parse_args()
    
    if args.threshold < 0 or args.threshold > 100:
        print("Error: Threshold must be between 0 and 100", file=sys.stderr)
        sys.exit(1)
    
    # Get matched results using the shared function
    print(f"Extracting C++ fields from: {args.cpp_file}")
    print(f"Extracting Java fields from: {args.java_file}")
    
    result = getMatchedResults(args.cpp_file, args.java_file, args.threshold)
    
    if result["cpp_fields_count"] == 0:
        print("No C++ fields found or error processing C++ file", file=sys.stderr)
        sys.exit(1)
    
    if result["java_fields_count"] == 0:
        print("No Java fields found or error processing Java file", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        # Load fields again for verbose output
        result["all_cpp_fields"] = load_cpp_fields(args.cpp_file)
        result["all_java_fields"] = load_java_fields(args.java_file)
    
    # Output results
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_json)
            print(f"Results saved to {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_json)
    
    # Print summary
    print(f"\nSummary:")
    print(f"C++ fields: {result['cpp_fields_count']}")
    print(f"Java fields: {result['java_fields_count']}")
    print(f"Matches found (≥{args.threshold}%): {result['matches_found']}")
    print(f"Match percentage: {result['java_fields_matched']}/{result['cpp_fields_count']} ({result['match_percentage']:.1f}%)")
    print(f"C++ fields matched: {result['cpp_fields_matched']}/{result['cpp_fields_count']}")
    print(f"Final result: {result['final_result'].upper()}")
    
    if result['matches']:
        print(f"\nTop matches:")
        for i, match in enumerate(result['matches'][:5]):  # Show top 5
            cpp_name = match['cpp_field']['name']
            java_name = match['java_field']['name']
            score = match['similarity_score']
            print(f"  {i+1}. {cpp_name} ↔ {java_name} ({score}%)")


if __name__ == "__main__":
    main()