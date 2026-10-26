# artemis-tools

Some scripts to prepare Artemis engine saves with your own lua payloads

- asb2iet.py - convert compiled .asb scripts back to .iet
- patch-save.py - replaces default save handler (`system/save.asb`) with `save:/inject.iet` embedded inside the save.
- read-save.py - decompresses the payload inside the save for inspection

## Useful repos

- https://github.com/sakarie9/pfs-rs - pack/unpack .pfs
- https://github.com/Gezine/ArtemisLuaLoader
- https://github.com/n0llptr/remote_lua_loader