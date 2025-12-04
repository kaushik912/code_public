### Prompt Used in Google Code Assist
generate a mermaid flow diagram. Do not use any special characters like "<," ">", ":",",",":",")","(","." in the mermaid code. Use underscore whenever applicable. Make sure the mermaid code works properly.

## Sample Response

```mermaid
graph LR
    subgraph isGitRepoInActive
        A[Start] --> B{Get User}
        B --> C{Get User Details}
        C --> D{Get Git Repo Details}
        D --> E{Get All Branches}
        E --> F{Get Commits}
        F --> G{Check InActive}
        G --> H{Save Fetch Time}
        H --> I{Save Fetch Result}
        I --> J{Return Result}
        J --> K{End}
    end
```