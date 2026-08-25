from typing import Optional
from pydantic import BaseModel, Field


class TelegramUser(BaseModel):
    id: int = Field(..., description="Unique identifier for this user or bot.")
    is_bot: bool = Field(..., description="True, if this user is a bot.")
    first_name: str = Field(..., description="User's or bot's first name.")
    last_name: Optional[str] = Field(None, description="User's or bot's last name.")
    username: Optional[str] = Field(None, description="User's or bot's username.")
    language_code: Optional[str] = Field(None, description="IETF language tag of the user's language.")


class TelegramChat(BaseModel):
    id: int = Field(..., description="Unique identifier for this chat.")
    type: str = Field(..., description="Type of chat, can be 'private', 'group', 'supergroup' or 'channel'.")
    title: Optional[str] = Field(None, description="Title, for supergroups, channels and group chats.")
    username: Optional[str] = Field(None, description="Username, for private chats, supergroups and channels if available.")
    first_name: Optional[str] = Field(None, description="First name of the other party in a private chat.")
    last_name: Optional[str] = Field(None, description="Last name of the other party in a private chat.")


class TelegramMessage(BaseModel):
    message_id: int = Field(..., description="Unique message identifier inside this chat.")
    from_user: Optional[TelegramUser] = Field(None, alias="from", description="Sender of the message; empty for messages sent to channels.")
    chat: TelegramChat = Field(..., description="Conversation the message belongs to.")
    date: int = Field(..., description="Date the message was sent in Unix time.")
    text: Optional[str] = Field(None, description="For text messages, the actual UTF-8 text of the message.")


class TelegramUpdate(BaseModel):
    update_id: int = Field(..., description="The update's unique identifier.")
    message: Optional[TelegramMessage] = Field(None, description="New incoming message of any kind.")
    edited_message: Optional[TelegramMessage] = Field(None, description="New version of a message.")
