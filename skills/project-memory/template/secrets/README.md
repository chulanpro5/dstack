# Secrets

Encrypted with git-crypt (see `../.gitattributes`). After a fresh clone, run
`git-crypt unlock <path-to-key>`. Keep the key in a password manager.

Refer to a file by its path. Never print, copy or paste its content into chat, logs, files or commits.
Before you push, run `git-crypt status -e`.

## <file name>

- **For:** <what it gives access to>
- **Load:** <how a tool reads it, for example `source secrets/<file>.env`>
