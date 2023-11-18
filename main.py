from rubpy import Client, Message, handlers
from rubpy import models, methods, exceptions
from rich.console import Console
from datetime import datetime
from asyncio import run

admins = [] # No need to edit this list

groups = [
    'g0DjNjc0eeaec8ae92ee9c9bfbdd3f95', # group one
    # '', # group two
    # and...
]

filters = [
    '@',
    'joinc',
    'joing'
    'rubika.ir'
]

console = Console()


async def updateAdmins(client: Client) -> None:
    global admins
    for guid in groups:
        results = await client(methods.groups.GetGroupAdminMembers(guid))
        for user in results.in_chat_members:
            if not user.member_guid in admins:
                admins.append(user.member_guid)
            else:
                continue


async def main():
    async with Client(session='.myAccount', timeout=20) as client:
        with console.status('bot in runing...') as status:
            await updateAdmins(client=client)
            for guid in groups:
                results = await client.get_group_info(group_guid=guid)
                group_name = results.group.group_title
                now = datetime.now()
                await client.send_message(
                    object_guid=guid,
                    message=f'the bot was successfully activated in chat {group_name}\n'
                            f'- time 『 {now.hour}:{now.minute}:{now.second} 』',
                )
            @client.on(handlers.MessageUpdates(models.is_group))
            async def updates(update: Message):

                for filter in filters:
                    if (
                            update.raw_text != None and
                            update.author_guid not in admins and
                            filter in update.raw_text
                    ):
                        await client.delete_messages(
                            object_guid=update.object_guid,
                            message_ids=update.message_id
                        )
                try:
                    if (
                            update.message.event_data.type == 'JoinedGroupByLink' or
                            update.message.event_data.type == 'AddedGroupMembers'
                    ):
                        message_id = update.message_id
                        results = await client.get_group_info(group_guid=update.object_guid)
                        group_name = results.group.group_title
                        await client.send_message(
                            object_guid=update.object_guid,
                            message=f'hello🖐🏻 welcome to {group_name} 💞💖',
                            reply_to_message_id=message_id
                        )
                    elif update.message.event_data.type == 'LeaveGroup':
                        message_id = update.message_id
                        await client.send_message(
                            object_guid=update.object_guid,
                            message='by 👋🏻👋🏻👋🏻',
                            reply_to_message_id=message_id
                        )
                except AttributeError:
                    pass


                if update.raw_text == 'test':
                    message_id = update.message_id
                    await client.send_message(
                        object_guid=update.object_guid,
                        message='The bot is active ✅',
                        reply_to_message_id=message_id
                    )


                elif update.raw_text == 'link':
                    message_id = update.message_id
                    results = await client(methods.groups.GetGroupLink(update.object_guid))
                    await client.send_message(
                        object_guid=update.object_guid,
                        message=f'`{results.join_link}`',
                        reply_to_message_id=message_id
                    )


                elif (
                    update.object_guid in groups and
                    update.author_guid in admins and
                    update.raw_text != None
                ):

                    if update.raw_text == 'open':
                        message_id = update.message_id
                        await client.set_group_default_access(
                            group_guid=update.object_guid,
                            access_list=['SendMessages']
                        )
                        await client.send_message(
                            object_guid=update.object_guid,
                            message='The group was successfully opened ✅',
                            reply_to_message_id=message_id
                        )


                    elif update.raw_text == 'close':
                        message_id = update.message_id
                        await client.set_group_default_access(
                            group_guid=update.object_guid,
                            access_list=[]
                        )
                        await client.send_message(
                            object_guid=update.object_guid,
                            message='The group was successfully closed ✅',
                            reply_to_message_id=message_id
                        )


                    elif update.raw_text == 'update-admins':
                        message_id = update.message_id
                        message = await client.send_message(
                            object_guid=update.object_guid,
                            message='Updating the list of admins...',
                            reply_to_message_id=message_id
                        )
                        await updateAdmins(client=client)
                        await message.edit('The list of admins has been updated ✅')


                    elif update.raw_text == 'ban':
                        message_id = update.message_id
                        if update.reply_message_id != None:
                            results = await client(methods.messages.GetMessagesByID(
                                update.object_guid, [update.reply_message_id])
                            )
                            user_guid = results.messages[0].author_object_guid
                            if not user_guid in admins:
                                await client.ban_group_member(
                                    group_guid=update.object_guid,
                                    member_guid=user_guid
                                )
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The user has been successfully removed from the group ✅',
                                    reply_to_message_id=message_id
                                )
                            else:
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The user is in the admin group❗',
                                    reply_to_message_id=message_id
                                )
                        else:
                            await client.send_message(
                                object_guid=update.object_guid,
                                message='Please reply to a message❗',
                                reply_to_message_id=message_id
                            )


                    elif update.raw_text.startswith('ban @'):
                        message_id = update.message_id
                        username = update.raw_text.split('@')[-1]
                        results = await client(methods.extras.GetObjectByUsername(username.lower()))
                        if not results.exist:
                            await client.send_message(
                                object_guid=update.object_guid,
                                message='Username is wrong❗',
                                reply_to_message_id=message_id
                            )
                        else:
                            user_guid = results.user.user_guid
                            if not user_guid in admins:
                                try:
                                    await client.ban_group_member(
                                        group_guid=update.object_guid,
                                        member_guid=user_guid
                                    )
                                except exceptions.InvalidAuth:
                                    await client.send_message(
                                        object_guid=update.object_guid,
                                        message='Please admin the robot account in the group❗',
                                        reply_to_message_id=message_id
                                    )
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The user has been successfully removed from the group ✅',
                                    reply_to_message_id=message_id
                                )
                            else:
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The user is in the admin group❗',
                                    reply_to_message_id=message_id
                                )


                    elif update.raw_text.startswith('timer'):
                        message_id = update.message_id
                        try:
                            time = int(update.raw_text.split()[-1])
                            if time == '':
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The entered information is not correct❗',
                                    reply_to_message_id=message_id
                                )
                            elif time > 3600:
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The timer cannot be more than 3600 seconds(one hour)❗',
                                    reply_to_message_id=message_id
                                )
                            else:
                                await client.set_group_timer(group_guid=update.object_guid, time=time)
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message=f'The timer was set to {time} seconds ✅',
                                    reply_to_message_id=message_id
                                )
                        except ValueError:
                            await client.send_message(
                                object_guid=update.object_guid,
                                message='The entered information is not correct❗',
                                reply_to_message_id=message_id
                            )


                    elif update.raw_text == 'unset-timer':
                        message_id = update.message_id
                        await client.set_group_timer(group_guid=update.object_guid, time=0)
                        await client.send_message(
                            object_guid=update.object_guid,
                            message='The timer went off ✅',
                            reply_to_message_id=message_id
                        )


                    elif update.raw_text == 'clear-black-list':
                        message_id = update.message_id
                        results = await client.get_banned_group_members(group_guid=update.object_guid)
                        for user in results.in_chat_members:
                            await client.unban_group_member(
                                group_guid=update.object_guid,
                                member_guid=user.member_guid
                            )
                        await client.send_message(
                            object_guid=update.object_guid,
                            message='The blacklist of the group was deleted ✅',
                            reply_to_message_id=message_id
                        )


                    elif update.raw_text == 'add-admin':
                        message_id = update.message_id
                        if update.reply_message_id != None:
                            results = await client(methods.messages.GetMessagesByID(
                                update.object_guid, [update.reply_message_id])
                            )
                            user_guid = results.messages[0].author_object_guid
                            if not user_guid in admins:
                                await client.set_group_admin(
                                    group_guid=update.object_guid,
                                    member_guid=user_guid,
                                    access_list=[
                                        'SetAdmin', 'ChangeInfo', 'BanMember',
                                        'PinMessages', 'SetJoinLink', 'SetMemberAccess',
                                        'DeleteGlobalAllMessages'
                                    ],
                                    action='SetAdmin'
                                )
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The user became an admin in the group ✅',
                                    reply_to_message_id=message_id
                                )
                            else:
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The user is now in the admin group❕',
                                    reply_to_message_id=message_id
                                )
                        else:
                            await client.send_message(
                                object_guid=update.object_guid,
                                message='Please reply to a message❗',
                                reply_to_message_id=message_id
                            )


                    elif update.raw_text.startswith('add-admin @'):
                        message_id = update.message_id
                        username = update.raw_text.split('@')[-1]
                        results = await client(methods.extras.GetObjectByUsername(username.lower()))
                        if not results.exist:
                            await client.send_message(
                                object_guid=update.object_guid,
                                message='Username is wrong❗',
                                reply_to_message_id=message_id
                            )
                        else:
                            user_guid = results.user.user_guid
                            if not user_guid in admins:
                                await client.set_group_admin(
                                    group_guid=update.object_guid,
                                    member_guid=user_guid,
                                    access_list=[
                                        'SetAdmin', 'ChangeInfo', 'BanMember',
                                        'PinMessages', 'SetJoinLink', 'SetMemberAccess',
                                        'DeleteGlobalAllMessages'
                                    ],
                                    action='SetAdmin'
                                )
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The user became an admin in the group ✅',
                                    reply_to_message_id=message_id
                                )
                            else:
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The user is now in the admin group❕',
                                    reply_to_message_id=message_id
                                )


                    elif update.raw_text == 'pin':
                        try:
                            await client.set_pin_message(
                                object_guid=update.object_guid,
                                message_id=update.reply_message_id,
                                action='Pin'
                            )
                            await client.send_message(
                                object_guid=update.object_guid,
                                message='The message has been pinned ✅',
                                reply_to_message_id=message_id
                            )
                        except:
                            await client.send_message(
                                object_guid=update.object_guid,
                                message='Please reply to a message❗',
                                reply_to_message_id=message_id
                            )


                    elif update.raw_text == 'un-pin':
                        message_id = update.message_id
                        try:
                            await client.unset_pin_message(
                                object_guid=update.object_guid,
                                message_id=update.reply_message_id,
                                action='Unpin'
                            )
                            await client.send_message(
                                object_guid=update.object_guid,
                                message='The message was unpinned ✅',
                                reply_to_message_id=message_id
                            )
                        except:
                            await client.send_message(
                                object_guid=update.object_guid,
                                message='Please reply to a message❗',
                                reply_to_message_id=message_id
                            )


                    elif update.raw_text == 'info':
                        message_id = update.message_id
                        await client.send_message(
                            object_guid=update.object_guid,
                            message='''
📌 Robot commands:

🔐 open group: `open`

🔓 close group: `close`

📌 pin message: `pin`(be sure to replay)

🚫📌 un pin message: `un-pin`(be sure to replay)

💼👤 set group admin: `add-admin`(be sure to replay)

💼👤 set group admin: `add-admin @id`

⏲ create timer: `timer 10`

🚫⏲ unset timer: `unset-timer`

🚫👤 ban user: `ban`(be sure to replay) or `ban @id`

💻 programmer: @khode_linux
                            ''',
                            reply_to_message_id=message_id
                        )


            await client.run_until_disconnected()


if __name__ == '__main__':
    run(main())
