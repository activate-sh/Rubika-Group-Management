from rubpy import Client, Message, handlers
from rubpy import models, methods, exceptions
from rich.console import Console
from os import system, uname
from asyncio import run

admins = []
groups = [
    'g0DjNjc0eeaec8ae92ee9c9bfbdd3f95'
]

console = Console()

def clearPage() -> None:
    if uname()[0] == 'Linux':
        system('clear')
    else:
        system('cls')


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
            await updateAdmins(client)
            for guid in groups:
                results = await client.get_group_info(group_guid=guid)
                group_name = results.group.group_title
                await client.send_message(
                    object_guid=guid,
                    message=f'the bot was successfully activated in chat {group_name}',
                )

            @client.on(handlers.MessageUpdates(models.is_group))
            async def updates(update: Message):
                if (
                    update.object_guid in groups and
                    update.author_guid in admins and
                    update.raw_text != None
                ):

                    if update.raw_text == 'open':
                        await client.set_group_default_access(
                            group_guid=update.object_guid,
                            access_list=['SendMessages']
                        )
                        await client.send_message(
                            object_guid=update.object_guid,
                            message='The group was successfully opened ✅',
                            reply_to_message_id=update.message_id
                        )


                    elif update.raw_text == 'close':
                        await client.set_group_default_access(
                            group_guid=update.object_guid,
                            access_list=[]
                        )
                        await client.send_message(
                            object_guid=update.object_guid,
                            message='The group was successfully closed ✅',
                            reply_to_message_id=update.message_id
                        )


                    elif update.raw_text == 'ban':
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
                                    reply_to_message_id=update.message_id
                                )
                            else:
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The user is in the admin group❗',
                                    reply_to_message_id=update.message_id
                                )
                        else:
                            await client.send_message(
                                object_guid=update.object_guid,
                                message='Please reply to a message❗',
                                reply_to_message_id=update.message_id
                            )


                    elif update.raw_text.startswith('ban @'):
                        username = update.raw_text.split('@')[-1]
                        results = await client(methods.extras.GetObjectByUsername(username.lower()))
                        if results.exist == False:
                            await client.send_message(
                                object_guid=update.object_guid,
                                message='Username is wrong❗',
                                reply_to_message_id=update.message_id
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
                                        reply_to_message_id=update.message_id
                                    )
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The user has been successfully removed from the group ✅',
                                    reply_to_message_id=update.message_id
                                )
                            else:
                                await client.send_message(
                                    object_guid=update.object_guid,
                                    message='The user is in the admin group❗',
                                    reply_to_message_id=update.message_id
                                )


            await client.run_until_disconnected()


if __name__ == '__main__':
    clearPage()
    run(main())
