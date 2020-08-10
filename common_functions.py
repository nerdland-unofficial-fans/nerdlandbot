def usernames_from_ids(ctx,list_users) -> list:
    usernames = []
    for user_id in list_users:
        try:
            # get user displayname based on ID in tracking table
            user = ctx.guild.get_member(int(user_id))
            usernames.append(user.display_name)
        except AttributeError:
            # if user not known on server, handle here
            print("could not find user with ID: " + user_id)
            pass
    return sorted(usernames)