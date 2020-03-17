## What's tested

If you're not uptodate with json validation schemas, here's what's tested

### Dialog template files

### Install files

### Talk files
- Checks that every values are either of type `object` or `array`
- In object type
  - Checks that `default` property is set, of type array with items of type string
  - Checks, if defined, that `short`property is of type array with items of type string
  - Checks that no additional properties are given
- In array type
  - Checks that items are of type string

### Config template files
- Checks that all config names start with a lowercase letter, contain only letters
- Checks that all configs have the following properties
  - `defaultValue` of type string
  - `dataType` of type string, allowed only [string, boolean, integer, list]
  - `isSensitive` of type boolean
  - `description` of type string, of minimun 10 characters lenght, starting with a capital letter
- Checks and allows the following optional properties and no other
  - `display` of type string. allowed only [hidden]
  - `beforeUpdate` of type string, starting with a small letter
  - `onUpdate` of type string, starting with a small letter
