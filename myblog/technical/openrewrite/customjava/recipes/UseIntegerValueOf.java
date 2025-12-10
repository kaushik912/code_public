/*
 * Copyright 2024 the original author or authors.
 * <p>
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * https://www.apache.org/licenses/LICENSE-2.0
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.yourorg;

import lombok.EqualsAndHashCode;
import lombok.Value;
import org.openrewrite.ExecutionContext;
import org.openrewrite.Recipe;
import org.openrewrite.TreeVisitor;
import org.openrewrite.java.JavaVisitor;
import org.openrewrite.java.JavaTemplate;
import org.openrewrite.java.tree.Expression;
import org.openrewrite.java.tree.J;
import org.openrewrite.java.tree.JavaType;

import java.util.List;

@Value
@EqualsAndHashCode(callSuper = false)
public class UseIntegerValueOf extends Recipe {

    @Override
    public String getDisplayName() {
        return "Use Integer.valueOf(x) or Integer.parseInt(x) instead of new Integer(x)";
    }

    @Override
    public String getDescription() {
        return "Replaces unnecessary boxing constructor calls with the more efficient Integer.valueOf(x) for int values, or Integer.parseInt(x) for String values.";
    }

    @Override
    public TreeVisitor<?, ExecutionContext> getVisitor() {
        return new JavaVisitor<ExecutionContext>() {
            private final JavaTemplate valueOfTemplate = JavaTemplate.builder("Integer.valueOf(#{any(int)})")
                    .build();

            private final JavaTemplate parseIntTemplate = JavaTemplate.builder("Integer.parseInt(#{any(String)})")
                    .build();

            @Override
            public J visitNewClass(J.NewClass newClass, ExecutionContext ctx) {
                J.NewClass n = (J.NewClass) super.visitNewClass(newClass, ctx);

                // Check if this is a new Integer() constructor
                if (n.getClazz() != null && n.getClazz().getType() != null) {
                    JavaType.FullyQualified type = (JavaType.FullyQualified) n.getClazz().getType();
                    if (type.getFullyQualifiedName().equals("java.lang.Integer")) {
                        List<Expression> arguments = n.getArguments();
                        if (arguments.size() == 1) {
                            Expression arg = arguments.get(0);

                            // Check constructor method type to determine which constructor is being called
                            if (n.getConstructorType() != null) {
                                List<JavaType> parameterTypes = n.getConstructorType().getParameterTypes();
                                if (!parameterTypes.isEmpty()) {
                                    JavaType paramType = parameterTypes.get(0);

                                    if (paramType instanceof JavaType.Primitive) {
                                        // Integer(int) constructor - use valueOf
                                        return valueOfTemplate.apply(getCursor(), n.getCoordinates().replace(), arg);
                                    } else if (paramType instanceof JavaType.Class) {
                                        JavaType.Class classType = (JavaType.Class) paramType;
                                        if (classType.getFullyQualifiedName().equals("java.lang.String")) {
                                            // Integer(String) constructor - use parseInt
                                            return parseIntTemplate.apply(getCursor(), n.getCoordinates().replace(), arg);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                return n;
            }
        };
    }
}
