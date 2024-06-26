import os
from enum import Enum

from .connection import Connection
from .event import BlockEvent, ChatEvent, ProjectileEvent

PoweredState = Enum('PoweredState', ['ON', 'OFF', 'TOGGLE'])


class CmdPositioner:
    def __init__(self, connection, packagePrefix, entityID):
        self.conn = connection
        self.pkg = packagePrefix
        self.entityID = entityID

    def getName(self):
        """Get entity name (entityId:int) => str"""
        return self.conn.sendReceive(b"entity.getName", self.entityID)

    def getPos(self):
        """Get entity position (entityId:int) => Vec3"""
        return self.conn.sendReceiveVec3(float, self.pkg + b".getPos", self.entityID)

    def setPos(self, *args):
        """Set entity position (entityId:int, x,y,z)"""
        self.conn.sendReceive(self.pkg + b".setPos", self.entityID, args)

    def getTilePos(self):
        """Get entity tile position (entityId:int) => Vec3"""
        return self.conn.sendReceiveVec3(int, self.pkg + b".getTile", self.entityID)

    def setTilePos(self, *args):
        """Set entity tile position (entityId:int) => Vec3"""
        self.conn.sendReceive(self.pkg + b".setTile", self.entityID, *args)

    def setDirection(self, *args):
        """Set entity direction (entityId:int, x,y,z)"""
        self.conn.sendReceive(self.pkg + b".setDirection", self.entityID, args)

    def getDirection(self):
        """Get entity direction (entityId:int) => Vec3"""
        return self.conn.sendReceiveVec3(float, self.pkg + b".getDirection", self.entityID)

    def setRotation(self, yaw):
        """Set entity rotation (entityId:int, yaw)"""
        self.conn.sendReceive(self.pkg + b".setRotation", self.entityID, yaw)

    def getRotation(self):
        """get entity rotation (entityId:int) => float"""
        return self.conn.sendReceiveScalar(float, self.pkg + b".getRotation", self.entityID)

    def setPitch(self, pitch):
        """Set entity pitch (entityId:int, pitch)"""
        self.conn.sendReceive(self.pkg + b".setPitch", self.entityID, pitch)

    def getPitch(self):
        """get entity pitch (entityId:int) => float"""
        return self.conn.sendReceiveScalar(float, self.pkg + b".getPitch", self.entityID)


class Entity(CmdPositioner):

    def __init__(self, connection, typeName, entityID):
        CmdPositioner.__init__(self, connection, b"entity", entityID)
        self.type = typeName

    def enableControl(self):
        """Enable control of entity (entityId:int)"""
        self.conn.sendReceive(self.pkg + b".enableControl", self.entityID)

    def disableControl(self):
        """Disable control of entity (entityId:int)"""
        self.conn.sendReceive(self.pkg + b".disableControl", self.entityID)

    def walkTo(self, *args):
        """Move entity (entityId:int, x,y,z)"""
        self.conn.sendReceive(self.pkg + b".walkTo", self.entityID, args)

    def remove(self):
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

    def setPos(self, *args):
        """Set camera entity position (x,y,z)"""
        self.conn.sendReceive(b"camera.setPos", args)


class CmdEvents:
    """Events"""

    def __init__(self, connection):
        self.conn = connection

    def clearAll(self):
        """Clear all old events"""
        self.conn.sendReceive(b"events.clear")

    def pollBlockHits(self):
        """Only triggered by sword => [BlockEvent]"""
        return self.conn.sendReceiveObjectList(BlockEvent.Hit, b"events.block.hits")

    def pollChatPosts(self):
        """Triggered by posts to chat => [ChatEvent]"""
        return self.conn.sendReceiveObjectList(ChatEvent.Post, b"events.chat.posts", maxsplit=2)

    def pollProjectileHits(self):
        """Only triggered by projectiles => [BlockEvent]"""
        return self.conn.sendReceiveObjectList(ProjectileEvent.Hit, b"events.projectile.hits")


class Minecraft:
    """The main class to interact with a running instance of Minecraft Pi."""

    def __init__(self, connection, playerName):
        self.conn = connection

        self.camera = CmdCamera(connection)
        self.player = Player(connection, playerName)
        self.events = CmdEvents(connection)
        self._playerName = playerName

    def getBlock(self, *args):
        """Get block (x,y,z) => id:int"""
        return self.conn.sendReceive(b"world.getBlock", args)

    def getBlockWithData(self, *args):
        """Get block with data (x,y,z) => Block"""
        return self.conn.sendReceiveList(b"world.getBlockWithData", args, sep=",")

    def getBlocks(self, *args):
        """Get a cuboid of blocks (x0,y0,z0,x1,y1,z1) => [id:int]"""
        return self.conn.sendReceiveList(b"world.getBlocks", *args, sep=",")

    def setBlock(self, *args):
        """Set block (x,y,z,id,[data])"""
        self.conn.sendReceive(b"world.setBlock", *args)

    def setBlocks(self, *args):
        """Set a cuboid of blocks (x0,y0,z0,x1,y1,z1,id,[data])"""
        self.conn.sendReceive(b"world.setBlocks", *args)

    def isBlockPassable(self, *args):
        """Check if block is passable (x,y,z) => Boolean"""
        return self.conn.sendReceiveBool(b"world.isBlockPassable", *args)

    def setPowered(self, *args, state=PoweredState.TOGGLE):
        """Set block powered (x,y,z,powered)"""
        self.conn.sendReceive(b"world.setPowered", *args, state)

    def setSign(self, *args):
        """Set a sign (x,y,z,sign_type,direction,line1,line2,line3,line4)
        direction: 0-north, 1-east, 2-south 3-west
        """
        self.conn.sendReceive(b"world.setSign", args)

    def spawnEntity(self, *args):
        """Spawn entity (x,y,z,id,[data])"""
        return Entity(self.conn, args[3], self.conn.sendReceive(b"world.spawnEntity", *args))

    def spawnParticle(self, *args):
        """Spawn entity (x,y,z,id,[data])"""
        return self.conn.sendReceive(b"world.spawnParticle", *args)

    def getNearbyEntities(self, *args):
        """get nearby entities (x,y,z)"""
        return self.conn.sendReceiveObjectList(
            lambda *attr: Entity(self.conn, *attr), b"world.getNearbyEntities", *args)

    def removeEntity(self, *args):
        """Spawn entity (x,y,z,id,[data])"""
        return self.conn.sendReceive(b"world.removeEntity", *args)

    def getHeight(self, *args):
        """Get the height of the world (x,y,z) => int"""
        return int(self.conn.sendReceive(b"world.getHeight", *args))

    def getPlayerEntityIds(self):
        """Get the entity ids of the connected players => [id]"""
        return self.conn.sendReceiveObjectList(lambda name, entityId: entityId, b"world.getPlayerIds")

    def getPlayerEntityId(self, name):
        """Get the entity id of the named player => id"""
        return self.conn.sendReceive(b"world.getPlayerId", name)

    def getPlayerNames(self):
        """Get the names of all currently connected players (or an empty List) => [str]"""
        return self.conn.sendReceiveObjectList(lambda name, entityId: name, b"world.getPlayerIds")

    def saveCheckpoint(self):
        """Save a checkpoint that can be used for restoring the world"""
        self.conn.sendReceive(b"world.checkpoint.save")

    def restoreCheckpoint(self):
        """Restore the world state to the checkpoint"""
        self.conn.sendReceive(b"world.checkpoint.restore")

    def postToChat(self, msg):
        """Post a message to the game chat"""
        self.conn.sendReceive(b"chat.post", msg)

    def setting(self, setting, status):
        """Set a world setting (setting, status). keys: world_immutable, nametags_visible"""
        self.conn.sendReceive(b"world.setting", setting, 1 if bool(status) else 0)

    def setPlayer(self, name):
        """Set the current player => bool"""
        if success := self.conn.sendReceiveBool(b"setPlayer", name):
            self._playerName = name
        else:
            self._playerName = None
        return success

    def getPlayerName(self):
        """Get the name of the previously set / currently attached player => str"""
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
