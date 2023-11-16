> ### _**amalgamation.py**_

*Prerequisites: `python3`.*

Make an amalgamation from a C/C++ source or header.\
Reduce file and dependency complexity more or less approximately.

### Usage
```sh
amalgamation
    [--root, -R]       set root directory (default .)
    --source, -S       set source file
    --target, -T       set target file
    [--include, -I]    add include path
    [--no-expand, -N]  skip amalgamation for a file
    [--verbose, -v]    set verbosity (default disabled)
```

### Test
```sh
./run_test.sh
```

### Debian / macOS
```sh
sudo -k cp amalgamation.py /usr/local/bin/amalgamation
```
