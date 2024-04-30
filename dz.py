# Static Folder Name
folder_name = "payapps"

dz_array = {
    "public": {
        "description": "PayGenius",
        "og_title": "PayGenius",
        "og_description": "PayGenius",
        "og_image": "https://payapps.dexignlab.com/django/social-image.png",
        "title": "PayGenius",
    },
    "global": {
        "css": [
            f"{folder_name}/vendor/jquery-nice-select/css/nice-select.css",
            f"{folder_name}/css/style.css",
        ],

        "js": {
            "top": [
                f"{folder_name}/vendor/global/global.min.js",
                f"{folder_name}/vendor/jquery-nice-select/js/jquery.nice-select.min.js",
            ],
            "bottom": [
                f"{folder_name}/js/custom.min.js",
                f"{folder_name}/js/dlabnav-init.js",
            ]
        },

    },
    "pagelevel": {
        "payapps": {  # AppName
            "payapps_views": {
                "css": {
                    "index": [],
                },
                "js": {
                    "index": [],
                },
            }
        }
    }
}
