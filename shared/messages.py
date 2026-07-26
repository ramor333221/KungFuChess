import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union
from shared.domain import MoveCommand
from config import constants


@dataclass
class LoginMessage:
    """DTO representing player authentication and login payloads."""
    username: str
    elo: int = constants.DEFAULT_ELO
    mode: str = constants.DEFAULT_MODE
    type: str = constants.MSG_TYPE_LOGIN

    def to_json(self) -> str:
        """Serialize login details to a JSON string."""
        return json.dumps({
            "type": self.type,
            "username": self.username,
            "elo": self.elo,
            "mode": self.mode
        })

    @classmethod
    def from_json(cls, json_str: str) -> "LoginMessage":
        """Deserialize a JSON string into a LoginMessage instance."""
        data = json.loads(json_str)
        return cls(
            username=data.get("username", constants.DEFAULT_PLAYER_NAME),
            elo=data.get("elo", constants.DEFAULT_ELO),
            mode=data.get("mode", constants.DEFAULT_MODE),
            type=data.get("type", constants.MSG_TYPE_LOGIN)
        )


@dataclass
class MoveMessage:
    """DTO representing game move commands exchanged over the network."""
    data: Union[MoveCommand, Dict[str, Any]]
    room_name: Optional[str] = None
    type: str = constants.MSG_TYPE_MOVE

    @classmethod
    def from_move_command(cls, move_command: MoveCommand, room_name: Optional[str] = None) -> "MoveMessage":
        """Factory method to create a MoveMessage from a strongly-typed MoveCommand."""
        return cls(
            type=constants.MSG_TYPE_MOVE,
            data={
                "from_row": move_command.from_row,
                "from_col": move_command.from_col,
                "to_row": move_command.to_row,
                "to_col": move_command.to_col
            },
            room_name=room_name
        )

    @classmethod
    def from_json(cls, json_str: str) -> "MoveMessage":
        """Deserialize a JSON string into a MoveMessage instance."""
        parsed = json.loads(json_str)
        return cls(
            type=parsed.get("type", constants.MSG_TYPE_MOVE),
            data=parsed.get("data"),
            room_name=parsed.get("room_name")
        )

    def get_move_command(self) -> Optional[MoveCommand]:
        """Extract and return a strongly-typed MoveCommand object from the internal data payload."""
        if isinstance(self.data, MoveCommand):
            return self.data
        if isinstance(self.data, dict):
            return MoveCommand(
                from_row=self.data.get("from_row"),
                from_col=self.data.get("from_col"),
                to_row=self.data.get("to_row"),
                to_col=self.data.get("to_col")
            )
        return None

    def to_json(self) -> str:
        """Serialize the move message to a JSON string for network transmission."""
        if isinstance(self.data, MoveCommand):
            data_dict = {
                "from_row": self.data.from_row,
                "from_col": self.data.from_col,
                "to_row": self.data.to_row,
                "to_col": self.data.to_col
            }
        elif isinstance(self.data, dict):
            data_dict = self.data
        else:
            data_dict = {}

        payload = {
            "type": self.type,
            "data": data_dict
        }
        if self.room_name:
            payload["room_name"] = self.room_name
        return json.dumps(payload)


@dataclass
class RoomMessage:
    """DTO representing room events, start triggers, disconnect alerts, and error messages."""
    type: str
    room_name: Optional[str] = None
    color: Optional[str] = None
    opponent: Optional[str] = None
    message: Optional[str] = None
    countdown: Optional[int] = None

    def to_json(self) -> str:
        """Serialize room event data to a JSON string."""
        payload = {"type": self.type}
        if self.room_name:
            payload["room_name"] = self.room_name
        if self.color:
            payload["color"] = self.color
        if self.opponent:
            payload["opponent"] = self.opponent
        if self.message:
            payload["message"] = self.message
        if self.countdown is not None:
            payload["countdown"] = self.countdown
        return json.dumps(payload)

    @classmethod
    def from_json(cls, json_str: str) -> "RoomMessage":
        """Deserialize a JSON string into a RoomMessage instance."""
        data = json.loads(json_str)
        return cls(
            type=data.get("type"),
            room_name=data.get("room_name") or data.get("room"),
            color=data.get("color"),
            opponent=data.get("opponent"),
            message=data.get("message"),
            countdown=data.get("countdown")
        )