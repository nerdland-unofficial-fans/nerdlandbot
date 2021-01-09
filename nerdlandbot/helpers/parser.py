
def parse_channel(channel_input: str) -> str:
    """
    Parses the first word of the input to a channel name.
    :param channel_input: The input string to parse to a channel name. (str)
    :return: The channel name, without any prefixes. (str)
    """

    # Channels don't contain spaces, remove extra words if necessary
    channel_name = channel_input.lower().split(' ')[0]

    # Convert to char array
    arr = list(channel_name)

    if arr[0] == '#':
        return ''.join(arr[1:])

    return ''.join(arr)
