import requests
import time

# ==============================
# TELEGRAM TOKEN
# ==============================

BOT_TOKEN = "8954668893:AAHDMiO09eJlUE84tnPj8HlSFPxIS39T4J4"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# ==============================
# MENU
# ==============================

MENU = {
    "pizza_1": ("Margherita Pizza", 199),
    "pizza_2": ("Farmhouse Pizza", 299),
    "pizza_3": ("Paneer Pizza", 279),

    "burger_1": ("Veg Burger", 99),
    "burger_2": ("Cheese Burger", 129),

    "drink_1": ("Cold Drink", 50),
    "drink_2": ("Lemonade", 60)
}


# ==============================
# USER DATA
# ==============================

users = {}


# ==============================
# TELEGRAM API
# ==============================

def telegram(method, data=None):

    url = f"{BASE_URL}/{method}"

    try:
        response = requests.post(
            url,
            data=data or {},
            timeout=10
        )

        return response.json()

    except Exception as e:
        print("Telegram error:", e)
        return None


# ==============================
# SEND MESSAGE
# ==============================

def send_message(chat_id, text, keyboard=None):

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:

        data["reply_markup"] = str({
            "inline_keyboard": keyboard
        }).replace("'", '"')

    return telegram("sendMessage", data)


# ==============================
# EDIT MESSAGE
# ==============================

def edit_message(chat_id, message_id, text, keyboard=None):

    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text
    }

    if keyboard:

        data["reply_markup"] = str({
            "inline_keyboard": keyboard
        }).replace("'", '"')

    return telegram("editMessageText", data)


# ==============================
# BUTTONS
# ==============================

def main_menu():

    return [
        [
            {
                "text": "🛒 Order Food",
                "callback_data": "order"
            }
        ],
        [
            {
                "text": "🍕 Menu",
                "callback_data": "menu"
            },
            {
                "text": "📍 Location",
                "callback_data": "location"
            }
        ],
        [
            {
                "text": "👨‍💼 Talk to Staff",
                "callback_data": "staff"
            }
        ]
    ]


def category_menu():

    return [
        [
            {
                "text": "🍕 Pizza",
                "callback_data": "cat_pizza"
            }
        ],
        [
            {
                "text": "🍔 Burger",
                "callback_data": "cat_burger"
            }
        ],
        [
            {
                "text": "🥤 Drinks",
                "callback_data": "cat_drinks"
            }
        ],
        [
            {
                "text": "🔙 Back",
                "callback_data": "home"
            }
        ]
    ]


def pizza_menu():

    return [
        [
            {
                "text": "Margherita - ₹199",
                "callback_data": "pizza_1"
            }
        ],
        [
            {
                "text": "Farmhouse - ₹299",
                "callback_data": "pizza_2"
            }
        ],
        [
            {
                "text": "Paneer - ₹279",
                "callback_data": "pizza_3"
            }
        ],
        [
            {
                "text": "🔙 Back",
                "callback_data": "order"
            }
        ]
    ]


def burger_menu():

    return [
        [
            {
                "text": "Veg Burger - ₹99",
                "callback_data": "burger_1"
            }
        ],
        [
            {
                "text": "Cheese Burger - ₹129",
                "callback_data": "burger_2"
            }
        ],
        [
            {
                "text": "🔙 Back",
                "callback_data": "order"
            }
        ]
    ]


def drinks_menu():

    return [
        [
            {
                "text": "Cold Drink - ₹50",
                "callback_data": "drink_1"
            }
        ],
        [
            {
                "text": "Lemonade - ₹60",
                "callback_data": "drink_2"
            }
        ],
        [
            {
                "text": "🔙 Back",
                "callback_data": "order"
            }
        ]
    ]


def quantity_menu():

    return [
        [
            {
                "text": "1",
                "callback_data": "qty_1"
            },
            {
                "text": "2",
                "callback_data": "qty_2"
            },
            {
                "text": "3",
                "callback_data": "qty_3"
            }
        ],
        [
            {
                "text": "4",
                "callback_data": "qty_4"
            },
            {
                "text": "5",
                "callback_data": "qty_5"
            },
            {
                "text": "10",
                "callback_data": "qty_10"
            }
        ]
    ]


# ==============================
# ANSWER BUTTON CLICK
# ==============================

def answer_callback(callback_id):

    telegram(
        "answerCallbackQuery",
        {
            "callback_query_id": callback_id
        }
    )


# ==============================
# HANDLE BUTTON
# ==============================

def handle_button(query):

    callback_id = query["id"]
    data = query["data"]

    chat_id = query["message"]["chat"]["id"]
    message_id = query["message"]["message_id"]

    answer_callback(callback_id)


    # --------------------------
    # HOME
    # --------------------------

    if data == "home":

        edit_message(
            chat_id,
            message_id,
            "🏠 Welcome!\n\nWhat would you like to do?",
            main_menu()
        )

        return


    # --------------------------
    # ORDER
    # --------------------------

    if data == "order":

        edit_message(
            chat_id,
            message_id,
            "🛒 Choose a category:",
            category_menu()
        )

        return


    # --------------------------
    # MENU
    # --------------------------

    if data == "menu":

        edit_message(
            chat_id,
            message_id,
            "🍽️ Choose a category:",
            category_menu()
        )

        return


    # --------------------------
    # CATEGORIES
    # --------------------------

    if data == "cat_pizza":

        edit_message(
            chat_id,
            message_id,
            "🍕 Choose your pizza:",
            pizza_menu()
        )

        return


    if data == "cat_burger":

        edit_message(
            chat_id,
            message_id,
            "🍔 Choose your burger:",
            burger_menu()
        )

        return


    if data == "cat_drinks":

        edit_message(
            chat_id,
            message_id,
            "🥤 Choose your drink:",
            drinks_menu()
        )

        return


    # --------------------------
    # LOCATION
    # --------------------------

    if data == "location":

        edit_message(
            chat_id,
            message_id,
            "📍 Main Market\nYour City\n\n🕐 Open: 10 AM - 10 PM",
            [
                [
                    {
                        "text": "🔙 Back",
                        "callback_data": "home"
                    }
                ]
            ]
        )

        return


    # --------------------------
    # STAFF
    # --------------------------

    if data == "staff":

        edit_message(
            chat_id,
            message_id,
            "👨‍💼 A staff member will help you shortly.",
            [
                [
                    {
                        "text": "🔙 Back",
                        "callback_data": "home"
                    }
                ]
            ]
        )

        return


    # --------------------------
    # ITEM SELECTED
    # --------------------------

    if data in MENU:

        item_name, price = MENU[data]

        users[chat_id] = {
            "item": item_name,
            "price": price,
            "quantity": 0,
            "state": "quantity"
        }

        edit_message(
            chat_id,
            message_id,
            f"""
🍽️ {item_name}

💰 Price: ₹{price}

How many would you like?
""",
            quantity_menu()
        )

        return


    # --------------------------
    # QUANTITY
    # --------------------------

    if data.startswith("qty_"):

        if chat_id not in users:

            edit_message(
                chat_id,
                message_id,
                "Please start a new order.",
                main_menu()
            )

            return


        quantity = int(data.split("_")[1])

        users[chat_id]["quantity"] = quantity
        users[chat_id]["state"] = "name"

        item = users[chat_id]["item"]
        price = users[chat_id]["price"]

        total = price * quantity

        edit_message(
            chat_id,
            message_id,
            f"""
✅ {item}
🔢 Quantity: {quantity}
💰 Total: ₹{total}

Now send your name.
"""
        )

        return


# ==============================
# HANDLE TEXT
# ==============================

def handle_text(chat_id, text):

    text = text.strip()

    if text == "/start":

        users.pop(chat_id, None)

        send_message(
            chat_id,
            "Namaste! 👋\n\nWelcome to our restaurant!",
            main_menu()
        )

        return


    if chat_id not in users:

        send_message(
            chat_id,
            "Please choose an option:",
            main_menu()
        )

        return


    user = users[chat_id]
    state = user.get("state")


    # --------------------------
    # NAME
    # --------------------------

    if state == "name":

        user["name"] = text
        user["state"] = "address"

        send_message(
            chat_id,
            "📍 Now send your delivery address."
        )

        return


    # --------------------------
    # ADDRESS
    # --------------------------

    if state == "address":

        user["address"] = text
        user["state"] = "confirm"

        total = user["price"] * user["quantity"]

        summary = f"""
🧾 ORDER SUMMARY

🍽️ {user["item"]}
🔢 Quantity: {user["quantity"]}
💰 Total: ₹{total}

👤 Name: {user["name"]}
📍 Address: {user["address"]}

Confirm your order?
"""

        keyboard = [
            [
                {
                    "text": "✅ Confirm",
                    "callback_data": "confirm"
                },
                {
                    "text": "❌ Cancel",
                    "callback_data": "cancel"
                }
            ]
        ]

        send_message(
            chat_id,
            summary,
            keyboard
        )

        return


    send_message(
        chat_id,
        "Please use the buttons above. 👆"
    )


# ==============================
# CONFIRM / CANCEL
# ==============================

def handle_confirm(chat_id, message_id, data):

    if chat_id not in users:

        edit_message(
            chat_id,
            message_id,
            "No active order.",
            main_menu()
        )

        return


    if data == "cancel":

        users.pop(chat_id, None)

        edit_message(
            chat_id,
            message_id,
            "❌ Order cancelled.",
            main_menu()
        )

        return


    if data == "confirm":

        user = users.pop(chat_id)

        total = user["price"] * user["quantity"]

        order_id = int(time.time())

        edit_message(
            chat_id,
            message_id,
            f"""
🎉 ORDER CONFIRMED!

🆔 Order #{order_id}

🍽️ {user["item"]}
🔢 Quantity: {user["quantity"]}
💰 Total: ₹{total}

👤 {user["name"]}
📍 {user["address"]}

Thank you! ❤️
"""
        )


# ==============================
# GET UPDATES
# ==============================

def get_updates(offset=None):

    params = {
        "timeout": 1
    }

    if offset is not None:
        params["offset"] = offset

    try:

        response = requests.get(
            f"{BASE_URL}/getUpdates",
            params=params,
            timeout=5
        )

        return response.json()

    except Exception as e:

        print("Update error:", e)

        return None


# ==============================
# MAIN LOOP
# ==============================

def main():

    print("🤖 Button Restaurant Bot Started!")

    offset = None

    while True:

        data = get_updates(offset)

        if not data:
            time.sleep(0.2)
            continue

        if not data.get("ok"):
            print(data)
            time.sleep(2)
            continue


        for update in data["result"]:

            offset = update["update_id"] + 1


            # BUTTON CLICK

            if "callback_query" in update:

                query = update["callback_query"]

                data_value = query["data"]

                chat_id = query["message"]["chat"]["id"]
                message_id = query["message"]["message_id"]


                if data_value in ["confirm", "cancel"]:

                    answer_callback(query["id"])

                    handle_confirm(
                        chat_id,
                        message_id,
                        data_value
                    )

                else:

                    handle_button(query)

                continue


            # TEXT MESSAGE

            message = update.get("message")

            if not message:
                continue


            chat_id = message["chat"]["id"]

            text = message.get("text", "")

            print(
                f"📩 {chat_id}: {text}"
            )

            handle_text(
                chat_id,
                text
            )


# ==============================
# START
# ==============================

if __name__ == "__main__":
    main()