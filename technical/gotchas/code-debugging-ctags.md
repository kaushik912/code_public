### Use ctags 
- install ctags in the remote system 
- it will allow you to navigate the code base.
- useful for debugging in production systems
- Usage
    - `ctags -R .`
    - Use the one below in case you want to restrict to Java code
        - `ctags -R --languages=Java --java-kinds=+p --fields=+l .` 
    - use vim to open the code
    - `Ctrl + ]` to jump to definition
    - `Ctrl+T` to go back  
    - `:E` to go back to directory
    