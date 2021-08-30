token = # bot token here

"""
Format:
reaction_roles = {
    messageId: [
        (emoji, roleId),
        (emoji, roleId)
    ],
    messageId: [
        (emoji, roleId)
    ]
}

e.g. 

reaction_roles = {
    999999999999999999: [  # test message 
        ("🔴", 999999999999999977),  # red circle, red roleid
        ("🔵", 999999999999999966),  # blue circle, blue roleid
    ],
    999999999999999988: [ 
        ("customemoji", 999999999999999955),
    ],
}

"""
