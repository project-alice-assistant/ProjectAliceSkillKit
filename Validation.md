# Validation

## dialog Templates

All dialogTemplates have three validation tests:
1) All dialog Templates have the same JSON Syntax, which is tested using the following JSON Schema [dialog-schema.json](https://github.com/project-alice-assistant/ProjectAliceSkillKit/blob/master/ProjectAliceSK/validate/src/schemas/dialog-schema.json).
2) The different translations should have the same slots (slotnames). The other settings of the slots like values ect. can be different.
3) There are no duplicates in the utterances. *Duplicates should not improve the performance, but from reports currently still improve it, so this is more of a warning*
4) Every slot used in the intents is either defined in the same dialogFile, a skill that is in the list of required skills of the installer, the core skills, or is a integrated slot of snips like *snips/numbers*
5) Every value used for a slot in the utterances either has to exists as value/synonym in the slot definition, or has to be automatically extensible

## talk Files

The talk files have two validation tests:
1) All talk files have the same JSON Syntax, which is tested using the following JSON Schema [talk-schema.json](https://github.com/project-alice-assistant/ProjectAliceSkillKit/blob/master/ProjectAliceSK/validate/src/schemas/talk-schema.json).
2) The language keys used in the different translations of the talk files are compared to find out whether a language key is missing in one of the files

## .install Installer Files
All installer files have the same JSON Syntax, which is tested using the following JSON Schema [install-schema.json](https://github.com/project-alice-assistant/ProjectAliceSkillKit/blob/master/ProjectAliceSK/validate/src/schemas/install-schema.json).
