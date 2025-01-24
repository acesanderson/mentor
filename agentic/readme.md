## Purpose of this directory
This is to build out a ReACT agent with the Curator and Mentor tools.

## Steps
- build a Chat object to experiment with different tools integrations + a workspace for storing + blacklisting + working on curations.
- abstract this to an Agentic workflow

## Detailed notes
- add tab completion to the chat object, for course titles, etc.


### Claude on tab completion using readline
```python
import readline

commands = ['help', 'hello', 'history', 'exit']

def completer(text, state):
    options = [cmd for cmd in commands if cmd.startswith(text)]
    return options[state] if state < len(options) else None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")
```
10k items is feasible for modern systems - the memory overhead is O(n) where n is the total length of all commands. The main performance impact would be in the string matching during completion, which is O(n) for each tab press. For better performance with large sets:

Use a prefix tree (trie) data structure
Or organize completions hierarchically (like git's subcommands)
Consider lazy loading if commands come from a database
