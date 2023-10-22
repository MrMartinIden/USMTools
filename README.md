# USMTools
(WIP)Set of tools to modify Ultimate Spider-man game.

Compatibility list:
Ultimate Spider-Man NTSC PS2

Function List:
Extraction

Make sure you are using 32-bit version of python.
To extract resource files from `*.PCPACK` you need to run the script `extrack_pcpack.py` like this:`python3-32 extrack_pcpack.py NAME_PAK.PCPACK`, where `NAME_PAK` - name of pcpack file. If the script was completed successfully, a directory with the same name as the pcpack file should be created in the same directory with the script. The created directory will contain the extracted resources. When changing them, be careful - the format and size of the files should be the same as before.

To re-importing the extracted resource files into `*.PCPACK`, you need run script `build_pcpack.py` like this:
`python3-32 build_pcpack.py NAME_PAK.PCPACK`, where `NAME_PAK` - name of original pcpack file. An important condition for re-import is that the directory with the extracted resource files must have the same name as the original pcpack file and must located with the script. After executing the script, a pcpack file should be created with the same name as the original, but with the extension `*._PCPACK`.
