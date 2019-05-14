## 0.4.5

### Misc
- Information about the pypi package has been added to the README.md
- Added 'Contents' block to the README.md and some fixes.

## 0.4.4

### Misc
- add test-upload target to Makefile

## 0.4.3

### Features
- added integration tests
- added automatic testing and build tools

### Fixes
- reformatted source code via 'black' tool

## 0.4.2

### Fixes
- fix map()

## 0.4.1

### Fixes
- fixed behavior when total > 1

## 0.4.0

### Features
- Add Evc.get_by_id() method
- Add Evc.get_first_item() method

### Fixes
- fix get_items()

### Misc
- added _id extraction from args[1]

## 0.3.1

### Fixes
- add try/except block for import simplejson

### Misc
- fix url in setup()
- fix author info in setup.cfg
- reformat LICENCE
- fix Copyright

## 0.3.0

### Fixes
- Allow "sort" param in get() method

## 0.2.0

### Features
- Add Evc.update() method

## 0.1.7

### Fixes
- fix W291 trailing whitespace

## 0.1.6

### Fixes
- Use json.dumps() only for params with "dict" type

## 0.1.5

### Fixes
- fix encoding of "params" argument for requests.get() method
- Add 'version' argument to kwargs_allowed list in get() function

### Misc
- Update README.rst

## 0.1.4

### Fixes
- Add support for 'max_results' and 'page' parameters in Evc.get() method

## 0.1.3

### Fixes
- Add calling delete() method in Evc.upsert() in case of empty parameter "data"

## 0.1.2

### Features
- Add Evc.upsert() method

## 0.1.1

- Refactoring

## 0.1

- Initial Release
