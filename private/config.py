token = "NzYwODc3MjMwNzk2MDQ2MzU2.X3ScJA.SbsvdwEYekqC5VpP0SseKtZn82w"

ROLE_CH = "818563318192930827"
TEST_CH = "872503667637506058"
ADMIN_ROLE_ID = "689940768189841425"

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
"""

reaction_roles = {
    880463045162303489: [  # test message in static-server-test
        ("🔴", 760831875899064360),  # red circle, red
        ("🔵", 760831928806408202),  # blue circle, blue
    ],
    880805280059891762: [ # signup message in serendipitous server
        ("ffquest", 713450325171896350), # FF quest icon, tempter of fate
    ],
}