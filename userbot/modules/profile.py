# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for changing your Telegram profile details. """

import os

from telethon.errors import ImageProcessFailedError, PhotoCropSizeSmallError
from telethon.errors.rpcerrorlist import (PhotoExtInvalidError,
                                          UsernameOccupiedError)
from telethon.tl.functions.account import (UpdateProfileRequest,
                                           UpdateUsernameRequest)
from telethon.tl.functions.photos import (DeletePhotosRequest,
                                          GetUserPhotosRequest,
                                          UploadProfilePhotoRequest)
from telethon.tl.types import InputPhoto, MessageMediaPhoto, User, Chat, Channel

from userbot import bot, CMD_HELP
from userbot.events import register, errors_handler
from datetime import datetime

# ====================== CONSTANT ===============================
INVALID_MEDIA = "```The extension of the media entity is invalid.```"
PP_CHANGED = "```Profile picture changed successfully.```"
PP_TOO_SMOL = "```This image is too small, use a bigger image.```"
PP_ERROR = "```Failure occured while processing image.```"

BIO_SUCCESS = "```Successfully edited Bio.```"

NAME_OK = "```Your name was succesfully changed.```"
USERNAME_SUCCESS = "```Your username was succesfully changed.```"
USERNAME_TAKEN = "```This username is already taken.```"
# ===============================================================


@register(outgoing=True, pattern="^.name")
@errors_handler
async def update_name(name):
    """ For .name command, change your name in Telegram. """
    if not name.text[0].isalpha() and name.text[0] not in ("/", "#", "@", "!"):
        newname = name.text[6:]
        if " " not in newname:
            firstname = newname
            lastname = ""
        else:
            namesplit = newname.split(" ", 1)
            firstname = namesplit[0]
            lastname = namesplit[1]

        await name.client(UpdateProfileRequest(
            first_name=firstname,
            last_name=lastname))
        await name.edit(NAME_OK)


@register(outgoing=True, pattern="^.setpfp$")
@errors_handler
async def set_profilepic(propic):
    """ For .profilepic command, change your profile picture in Telegram. """
    if not propic.text[0].isalpha() and propic.text[0] not in ("/", "#", "@", "!"):
        replymsg = await propic.get_reply_message()
        photo = None
        if replymsg.media:
            if isinstance(replymsg.media, MessageMediaPhoto):
                photo = await propic.client.download_media(message=replymsg.photo)
            elif "image" in replymsg.media.document.mime_type.split('/'):
                photo = await propic.client.download_file(replymsg.media.document)
            else:
                await propic.edit(INVALID_MEDIA)

        if photo:
            try:
                await propic.client(UploadProfilePhotoRequest(
                    await propic.client.upload_file(photo)
                ))
                os.remove(photo)
                await propic.edit(PP_CHANGED)
            except PhotoCropSizeSmallError:
                await propic.edit(PP_TOO_SMOL)
            except ImageProcessFailedError:
                await propic.edit(PP_ERROR)
            except PhotoExtInvalidError:
                await propic.edit(INVALID_MEDIA)


@register(outgoing=True, pattern="^.setbio (.*)")
@errors_handler
async def set_biograph(setbio):
    """ For .setbio command, set a new bio for your profile in Telegram. """
    if not setbio.text[0].isalpha() and setbio.text[0] not in ("/", "#", "@", "!"):
        newbio = setbio.pattern_match.group(1)
        await setbio.client(UpdateProfileRequest(about=newbio))
        await setbio.edit(BIO_SUCCESS)


@register(outgoing=True, pattern="^.username (.*)")
@errors_handler
async def update_username(username):
    """ For .username command, set a new username in Telegram. """
    if not username.text[0].isalpha() and username.text[0] not in ("/", "#", "@", "!"):
        newusername = username.pattern_match.group(1)
        try:
            await username.client(UpdateUsernameRequest(newusername))
            await username.edit(USERNAME_SUCCESS)
        except UsernameOccupiedError:
            await username.edit(USERNAME_TAKEN)

@register(outgoing=True, pattern="^.count")
@errors_handler
async def _(event):
    if event.fwd_from:
        return
    start = datetime.now()
    u = 0
    g = 0
    c = 0
    bc = 0
    b = 0
    dialogs = await bot.get_dialogs(
        limit=None,
        ignore_migrated=True
    )
    for d in dialogs:
        currrent_entity = d.entity
        if type(currrent_entity) is User:
            if currrent_entity.bot:
                b += 1
            else:
                u += 1
        elif type(currrent_entity) is Chat:
            g += 1
        elif type(currrent_entity) is Channel:
            if currrent_entity.broadcast:
                bc += 1
            else:
                c += 1
        else:
            print(d)
    end = datetime.now()
    ms = (end - start).seconds
    await event.edit("""Obtained in {} seconds.
Users:\t{}
Groups:\t{}
Super Groups:\t{}
Channels:\t{}
Bots:\t{}""".format(ms, u, g, c, bc, b))

@register(outgoing=True, pattern=r"^.delpfp")
@errors_handler
async def remove_profilepic(delpfp):
    """ For .delpfp command, delete your current profile picture in Telegram. """
    if not delpfp.text[0].isalpha() and delpfp.text[0] not in ("/", "#", "@", "!"):
        group = delpfp.text[8:]
        if group == 'all':
            lim = 0
        elif group.isdigit():
            lim = int(group)
        else:
            lim = 1

        pfplist = await delpfp.client(GetUserPhotosRequest(
            user_id=delpfp.from_id,
            offset=0,
            max_id=0,
            limit=lim))
        input_photos = []
        for sep in pfplist.photos:
            input_photos.append(
                InputPhoto(
                    id=sep.id,
                    access_hash=sep.access_hash,
                    file_reference=sep.file_reference
                )
            )
        await delpfp.client(DeletePhotosRequest(id=input_photos))
        await delpfp.edit(f"`Successfully deleted {len(input_photos)} profile picture(s).`")

CMD_HELP.update({
    "profile": ".username <new_username>\
\nUsage: Changes your Telegram username.\
\n\n.name <firstname> or .name <firstname> <lastname>\
\nUsage: Changes your Telegram name.(First and last name will get split by the first space)\
\n\n.setpfp\
\nUsage: Reply with .setpfp to an image to change your Telegram profie picture.\
\n\n.setbio <new_bio>\
\nUsage: Changes your Telegram bio.\
\n\n.delpfp or .delpfp <number>/<all>\
\nUsage: Deletes your Telegram profile picture(s).\
\n\n.count\
\nUsage: Counts your groups, chats, bots etc..."
})
