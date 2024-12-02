import os
from enum import Enum
from typing import Union, overload, List, Optional, Tuple

from mcpi.vec3 import Vec3
from .connection import Connection
from .event import BlockEvent, ChatEvent, ProjectileEvent

PoweredState = Enum('PoweredState', ['ON', 'OFF', 'TOGGLE'])


class CmdPositioner:
    def __init__(self, connection, packagePrefix, entityID):
        self.conn = connection
        self.pkg = packagePrefix
        self.entityID = entityID

    def getName(self) -> str:
        """Get entity name"""
        return self.conn.sendReceive(b"entity.getName", self.entityID)

    def getPos(self) -> Vec3:
        """Get entity position"""
        return self.conn.sendReceiveVec3(float, self.pkg + b".getPos", self.entityID)

    @overload
    def setPos(self, vec: Vec3) -> None: ...

    @overload
    def setPos(self, x: int, y: int, z: int) -> None: ...

    def setPos(self, *args: Union[Vec3, int]) -> None:
        """Set entity position"""
        self.conn.sendReceive(self.pkg + b".setPos", self.entityID, args)

    def getTilePos(self) -> Vec3:
        """Get entity tile position"""
        return self.conn.sendReceiveVec3(int, self.pkg + b".getTile", self.entityID)

    @overload
    def setTilePos(self, vec: Vec3) -> None: ...

    @overload
    def setTilePos(self, x: int, y: int, z: int) -> None: ...

    def setTilePos(self, *args: Union[Vec3, int]) -> None:
        """Set entity tile position"""
        self.conn.sendReceive(self.pkg + b".setTile", self.entityID, *args)

    @overload
    def setDirection(self, vec: Vec3) -> None: ...

    @overload
    def setDirection(self, x: int, y: int, z: int) -> None: ...

    def setDirection(self, *args) -> None:
        """Set entity direction"""
        self.conn.sendReceive(self.pkg + b".setDirection", self.entityID, args)

    def getDirection(self) -> Vec3:
        """Get entity direction"""
        return self.conn.sendReceiveVec3(float, self.pkg + b".getDirection", self.entityID)

    def getHeldItem(self) -> str:
        """Get entity held item"""
        return self.conn.sendReceiveList(self.pkg + b".getHeldItem", self.entityID, sep=",")

    def setRotation(self, yaw: float) -> None:
        """Set entity rotation (entityId:int, yaw)"""
        self.conn.sendReceive(self.pkg + b".setRotation", self.entityID, yaw)

    def getRotation(self) -> float:
        """Get entity rotation"""
        return self.conn.sendReceiveScalar(float, self.pkg + b".getRotation", self.entityID)

    def setPitch(self, pitch: float) -> None:
        """Set entity pitch"""
        self.conn.sendReceive(self.pkg + b".setPitch", self.entityID, pitch)

    def getPitch(self) -> float:
        """get entity pitch"""
        return self.conn.sendReceiveScalar(float, self.pkg + b".getPitch", self.entityID)


class Entity(CmdPositioner):

    def __init__(self, connection, typeName, entityID):
        CmdPositioner.__init__(self, connection, b"entity", entityID)
        self.type = typeName

    def enableControl(self) -> None:
        """Enable control of entity"""
        self.conn.sendReceive(self.pkg + b".enableControl", self.entityID)

    def disableControl(self) -> None:
        """Disable control of entity"""
        self.conn.sendReceive(self.pkg + b".disableControl", self.entityID)

    @overload
    def walkTo(self, vec: Vec3) -> None: ...

    @overload
    def walkTo(self, x: int, y: int, z: int) -> None: ...

    def walkTo(self, *args: Union[Vec3, int]) -> None:
        """Move entity"""
        self.conn.sendReceive(self.pkg + b".walkTo", self.entityID, args)

    def remove(self) -> None:
        self.conn.sendReceive(b"entity.remove", self.entityID)


class Player(CmdPositioner):

    def __init__(self, connection, playerName):
        CmdPositioner.__init__(self, connection, b"player", playerName)
        self.conn = connection

    def performCommand(self, command: str) -> bool:
        """Make the player perform the given command.

        Returns:
            True if the command was successful, otherwise False
        """
        return self.conn.sendReceiveBool(self.pkg + b".performCommand", command)


class CmdCamera:
    def __init__(self, connection):
        self.conn = connection

    def setNormal(self, *args):
        """Set camera mode to normal Minecraft view ([entityId])"""
        self.conn.sendReceive(b"camera.mode.setNormal", args)

    def setFixed(self):
        """Set camera mode to fixed view"""
        self.conn.sendReceive(b"camera.mode.setFixed")

    def setFollow(self, *args):
        """Set camera mode to follow an entity ([entityId])"""
        self.conn.sendReceive(b"camera.mode.setFollow", args)

    @overload
    def setPos(self, vec: Vec3) -> None: ...

    @overload
    def setPos(self, x: int, y: int, z: int) -> None: ...

    def setPos(self, *args: Union[Vec3, int]) -> None:
        """Set camera entity position"""
        self.conn.sendReceive(b"camera.setPos", args)


class CmdEvents:
    """Events"""

    def __init__(self, connection):
        self.conn = connection

    def clearAll(self) -> None:
        """Clear all old events"""
        self.conn.sendReceive(b"events.clear")

    def pollBlockHits(self) -> List[BlockEvent]:
        """Only triggered by sword"""
        return self.conn.sendReceiveObjectList(BlockEvent.Hit, b"events.block.hits")

    def pollChatPosts(self) -> List[ChatEvent]:
        """Triggered by posts to chat"""
        return self.conn.sendReceiveObjectList(ChatEvent.Post, b"events.chat.posts", maxsplit=2)

    def pollProjectileHits(self) -> List[BlockEvent]:
        """Only triggered by projectiles"""
        return self.conn.sendReceiveObjectList(ProjectileEvent.Hit, b"events.projectile.hits")


class Minecraft:
    """The main class to interact with a running instance of Minecraft Pi."""

    def __init__(self, connection, playerName):
        self.conn = connection

        self.camera = CmdCamera(connection)
        self.player = Player(connection, playerName)
        self.events = CmdEvents(connection)
        self._playerName = playerName

    @overload
    def getBlock(self, vec: Vec3) -> str: ...

    @overload
    def getBlock(self, x: int, y: int, z: int) -> str: ...

    def getBlock(self, *args: Union[Vec3, int]) -> str:
        """Get block"""
        return self.conn.sendReceive(b"world.getBlock", args)

    @overload
    def getBlockWithData(self, vec: Vec3) -> Tuple[str, str]: ...

    @overload
    def getBlockWithData(self, x: int, y: int, z: int) -> Tuple[str, str]: ...

    def getBlockWithData(self, *args: Union[Vec3, int]) -> tuple[str, dict[str, str]]:
        """Get block with data"""
        data = self.conn.sendReceiveList(b"world.getBlockWithData", args, sep=",")
        block_data = {}
        if len(data) > 1 and data[1]:
            for d in data[1:]:
                key, value = d.split("=", 1)
                block_data[key] = value
        return data[0], block_data

    @overload
    def getBlocks(self, vec0: Vec3, vec1: Vec3) -> List[str]: ...

    @overload
    def getBlocks(self, x0: int, y0: int, z0: int, x1: int, y1: int, z1: int) -> List[str]: ...

    def getBlocks(self, *args: Union[Vec3, int]) -> List[str]:
        """Get a cuboid of blocks"""
        return self.conn.sendReceiveList(b"world.getBlocks", *args, sep=",")

    @overload
    def setBlock(self, vec: Vec3, material: str, facing: int) -> None: ...
    @overload
    def setBlock(self, vec: Vec3, material: str) -> None: ...
    @overload
    def setBlock(self, vec: Vec3) -> None: ...

    @overload
    def setBlock(self, x: int, y: int, z: int, material: str, facing: int) -> None: ...
    @overload
    def setBlock(self, x: int, y: int, z: int, material: str) -> None: ...
    @overload
    def setBlock(self, x: int, y: int, z: int) -> None: ...

    def setBlock(self, *args) -> None:
        """Set block"""
        self.conn.sendReceive(b"world.setBlock", *args)

    @overload
    def setBlocks(self, vec0: Vec3, vec1: Vec3, material: str, facing: int) -> None: ...
    @overload
    def setBlocks(self, vec0: Vec3, vec1: Vec3, material: str) -> None: ...
    @overload
    def setBlocks(self, vec0: Vec3, vec1: Vec3) -> None: ...

    @overload
    def setBlocks(self, x0: int, y0: int, z0: int, x1: int, y1: int, z1: int, material: str, facing: int) -> None: ...
    @overload
    def setBlocks(self, x0: int, y0: int, z0: int, x1: int, y1: int, z1: int, material: str) -> None: ...
    @overload
    def setBlocks(self, x0: int, y0: int, z0: int, x1: int, y1: int, z1: int) -> None: ...

    def setBlocks(self, *args) -> None:
        """Set a cuboid of blocks"""
        self.conn.sendReceive(b"world.setBlocks", *args)

    @overload
    def isBlockPassable(self, vec: Vec3) -> bool: ...

    @overload
    def isBlockPassable(self, x: int, y: int, z: int) -> bool: ...

    def isBlockPassable(self, *args: Union[Vec3, int]) -> bool:
        """Check if block is passable"""
        return self.conn.sendReceiveBool(b"world.isBlockPassable", *args)

    @overload
    def setPowered(self, vec: Vec3, state: PoweredState) -> None: ...

    @overload
    def setPowered(self, x: int, y: int, z: int, state: PoweredState) -> None: ...

    def setPowered(self, *args: Union[Vec3, int], state=PoweredState.TOGGLE) -> None:
        """Set block powered"""
        self.conn.sendReceive(b"world.setPowered", *args, state)

    @overload
    def setSign(self, vec: Vec3, material: Optional[str], facing: int, line1: str, line2: str, line3: str, line4: str) -> None: ...
    @overload
    def setSign(self, vec: Vec3, material: Optional[str], facing: int) -> None: ...
    @overload
    def setSign(self, vec: Vec3, material: Optional[str]) -> None: ...
    @overload
    def setSign(self, vec: Vec3) -> None: ...

    @overload
    def setSign(self, x: int, y: int, z: int, material: Optional[str], facing: int, line1: str, line2: str, line3: str, line4: str) -> None: ...
    @overload
    def setSign(self, x: int, y: int, z: int, material: Optional[str], facing: int) -> None: ...
    @overload
    def setSign(self, x: int, y: int, z: int, material: Optional[str]) -> None: ...
    @overload
    def setSign(self, x: int, y: int, z: int) -> None: ...

    def setSign(self, *args) -> None:
        """Set a sign"""
        self.conn.sendReceive(b"world.setSign", args)

    @overload
    def spawnEntity(self, vec: Vec3, entityType: str) -> None: ...
    @overload
    def spawnEntity(self, vec: Vec3) -> None: ...

    @overload
    def spawnEntity(self, x: int, y: int, z: int, entityType: str) -> None: ...
    @overload
    def spawnEntity(self, x: int, y: int, z: int) -> None: ...

    def spawnEntity(self, *args) -> Entity:
        """Spawn entity"""
        return Entity(self.conn, args[3], self.conn.sendReceive(b"world.spawnEntity", *args))

    @overload
    def spawnParticle(self, vec: Vec3, particleType: str) -> None: ...
    @overload
    def spawnParticle(self, vec: Vec3) -> None: ...

    @overload
    def spawnParticle(self, x: int, y: int, z: int, particleType: str) -> None: ...
    @overload
    def spawnParticle(self, x: int, y: int, z: int) -> None: ...

    def spawnParticle(self, *args):
        """Spawn entity"""
        return self.conn.sendReceive(b"world.spawnParticle", *args)

    @overload
    def getNearbyEntities(self, vec: Vec3) -> List[Entity]: ...

    @overload
    def getNearbyEntities(self, x: int, y: int, z: int) -> List[Entity]: ...

    def getNearbyEntities(self, *args: Union[Vec3, int]) -> List[Entity]:
        """Get nearby entities"""
        return self.conn.sendReceiveObjectList(
            lambda *attr: Entity(self.conn, *attr), b"world.getNearbyEntities", *args)

    def removeEntity(self, *args) -> None:
        """Remove entity"""
        return self.conn.sendReceive(b"world.removeEntity", *args)

    @overload
    def getHeight(self, vec: Vec3) -> int: ...

    @overload
    def getHeight(self, x: int, y: int, z: int) -> int: ...

    def getHeight(self, *args: Union[Vec3, int]) -> int:
        """Get the height of the world"""
        return int(self.conn.sendReceive(b"world.getHeight", *args))

    def getPlayerEntityIds(self) -> List[str]:
        """Get the entity ids of the connected players"""
        return self.conn.sendReceiveObjectList(lambda name, entityId: entityId, b"world.getPlayerIds")

    def getPlayerEntityId(self, name: str) -> str:
        """Get the entity id of the named player"""
        return self.conn.sendReceive(b"world.getPlayerId", name)

    def getPlayerNames(self) -> List[str]:
        """Get the names of all currently connected players (or an empty List)"""
        return self.conn.sendReceiveObjectList(lambda name, entityId: name, b"world.getPlayerIds")

    def saveCheckpoint(self) -> None:
        """Save a checkpoint that can be used for restoring the world"""
        self.conn.sendReceive(b"world.checkpoint.save")

    def restoreCheckpoint(self) -> None:
        """Restore the world state to the checkpoint"""
        self.conn.sendReceive(b"world.checkpoint.restore")

    def postToChat(self, msg: str) -> None:
        """Post a message to the game chat"""
        self.conn.sendReceive(b"chat.post", msg)

    def setting(self, setting, status) -> None:
        """Set a world setting (setting, status). keys: world_immutable, nametags_visible"""
        self.conn.sendReceive(b"world.setting", setting, 1 if bool(status) else 0)

    def setPlayer(self, name: str) -> bool:
        """Set the current player"""
        if success := self.conn.sendReceiveBool(b"setPlayer", name):
            self._playerName = name
        else:
            self._playerName = None
        return success

    def getPlayerName(self) -> Optional[str]:
        """Get the name of the previously set / currently attached player"""
        if self._playerName:
            return self._playerName
        else:
            p = self.conn.sendReceive(b"getPlayer")
            return None if p == "(none)" else p

    playerName = property(getPlayerName)

    def performCommand(self, command: str) -> bool:
        """Execute the given command on the console.

        Returns:
            True if the command was successful, otherwise False
        """
        return self.conn.sendReceiveBool(b"console.performCommand", command)

    @staticmethod
    def create(address="localhost", port=4711, playerName=None, debug=False):
        if "JRP_API_HOST" in os.environ:
            address = os.environ["JRP_API_HOST"]
        if "JRP_API_PORT" in os.environ:
            try:
                port = int(os.environ["JRP_API_PORT"])
            except ValueError:
                pass

        return Minecraft(Connection(address, port, debug), playerName)


def mcpy(func):
    # these will be created as global variable in module, so not good idea
    # func.__globals__['mc'] = Minecraft.create()
    # func.__globals__['pos'] = func.__globals__['mc'].player.getTilePos()
    # func.__globals__['direction'] = func.__globals__['mc'].player.getDirection()
    func.__doc__ = ("_mcpy :" + func.__doc__) if func.__doc__ else "_mcpy "
    return func


if __name__ == "__main__":
    mc = Minecraft.create()
    mc.postToChat("Hello, Minecraft!")
