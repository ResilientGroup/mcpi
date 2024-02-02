import os
import math

from .connection import Connection
from .event import BlockEvent, ChatEvent, ProjectileEvent
from .util import flatten
from enum import Enum

PoweredState = Enum('PoweredState', ['ON', 'OFF', 'TOGGLE'])

def _intFloor(*args):
    return [int(math.floor(x)) for x in flatten(args)]

class CmdPositioner:
    """Methods for setting and getting positions"""
    def __init__(self, connection, packagePrefix):
        self.conn = connection
        self.pkg = packagePrefix

    def getPos(self, id):
        """Get entity position (entityId:int) => Vec3"""
        return self.conn.sendReceiveVec3(float, self.pkg + b".getPos", id)

    def setPos(self, id, *args):
        """Set entity position (entityId:int, x,y,z)"""
        self.conn.sendReceive(self.pkg + b".setPos", id, args)

    def getTilePos(self, id):
        """Get entity tile position (entityId:int) => Vec3"""
        return self.conn.sendReceiveVec3(int, self.pkg + b".getTile", id)

    def setTilePos(self, id, *args):
        """Set entity tile position (entityId:int) => Vec3"""
        self.conn.sendReceive(self.pkg + b".setTile", id, _intFloor(*args))

    def setDirection(self, id, *args):
        """Set entity direction (entityId:int, x,y,z)"""
        self.conn.sendReceive(self.pkg + b".setDirection", id, args)

    def getDirection(self, id):
        """Get entity direction (entityId:int) => Vec3"""
        return self.conn.sendReceiveVec3(float, self.pkg + b".getDirection", id)

    def setRotation(self, id, yaw):
        """Set entity rotation (entityId:int, yaw)"""
        self.conn.sendReceive(self.pkg + b".setRotation", id, yaw)

    def getRotation(self, id):
        """get entity rotation (entityId:int) => float"""
        return self.conn.sendReceiveScalar(float, self.pkg + b".getRotation", id)

    def setPitch(self, id, pitch):
        """Set entity pitch (entityId:int, pitch)"""
        self.conn.sendReceive(self.pkg + b".setPitch", id, pitch)

    def getPitch(self, id):
        """get entity pitch (entityId:int) => float"""
        return self.conn.sendReceiveScalar(float, self.pkg + b".getPitch", id)

    def setting(self, setting, status):
        """Set a player setting (setting, status). keys: autojump"""
        self.conn.sendReceive(self.pkg + b".setting", setting, 1 if bool(status) else 0)

class CmdEntity(CmdPositioner):
    """Methods for entities"""
    def __init__(self, connection):
        CmdPositioner.__init__(self, connection, b"entity")
    
    def getName(self, id):
        """Get the list name of the player with entity id => [name:str]
        
        Also can be used to find name of entity if entity is not a player."""
        return self.conn.sendReceive(b"entity.getName", id)

    def enableControl(self, id):
        """Enable control of entity (entityId:int)"""
        self.conn.sendReceive(self.pkg + b".enableControl", id)

    def disableControl(self, id):
        """Disable control of entity (entityId:int)"""
        self.conn.sendReceive(self.pkg + b".disableControl", id)

    def walkTo(self, id, *args):
        """Move entity (entityId:int, x,y,z)"""
        self.conn.sendReceive(self.pkg + b".walkTo", id, args)

    def remove(self, id):
        self.conn.sendReceive(b"entity.remove", id)


class Entity:
    def __init__(self, conn, typeName, entity_uuid):
        self.p = CmdEntity(conn)
        self.type = typeName
        self.id = entity_uuid
    def getPos(self):
        return self.p.getPos(self.id)
    def setPos(self, *args):
        return self.p.setPos(self.id, args)
    def enableControl(self):
        return self.p.enableControl(self.id)
    def disableControl(self):
        return self.p.disableControl(self.id)
    def walkTo(self, *args):
        return self.p.walkTo(self.id, args)
    def getTilePos(self):
        return self.p.getTilePos(self.id)
    def setTilePos(self, *args):
        return self.p.setTilePos(self.id, args)
    def setDirection(self, *args):
        return self.p.setDirection(self.id, args)
    def getDirection(self):
        return self.p.getDirection(self.id)
    def setRotation(self, yaw):
        return self.p.setRotation(self.id, yaw)
    def getRotation(self):
        return self.p.getRotation(self.id)
    def setPitch(self, pitch):
        return self.p.setPitch(self.id, pitch)
    def getPitch(self):
        return self.p.getPitch(self.id)
    def remove(self):
        self.p.conn.sendReceive(b"entity.remove", self.id)


class CmdPlayer(CmdPositioner):
    """Methods for the host (Raspberry Pi) player"""
    def __init__(self, connection, playerName):
        CmdPositioner.__init__(self, connection,  b"player")
        self.conn = connection
        self.playerName = playerName

    def getPos(self):
        return CmdPositioner.getPos(self, self.playerName)
    def setPos(self, *args):
        return CmdPositioner.setPos(self, self.playerName, args)
    def getTilePos(self):
        return CmdPositioner.getTilePos(self, self.playerName)
    def setTilePos(self, *args):
        return CmdPositioner.setTilePos(self, self.playerName, args)
    def setDirection(self, *args):
        return CmdPositioner.setDirection(self, self.playerName, args)
    def getDirection(self):
        return CmdPositioner.getDirection(self, self.playerName)
    def setRotation(self, yaw):
        return CmdPositioner.setRotation(self,self.playerName, yaw)
    def getRotation(self):
        return CmdPositioner.getRotation(self, self.playerName)
    def setPitch(self, pitch):
        return CmdPositioner.setPitch(self, self.playerName, pitch)
    def getPitch(self):
        return CmdPositioner.getPitch(self, self.playerName)

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
        self.entity = CmdEntity(connection)
        self.player = CmdPlayer(connection, playerName)
        self.events = CmdEvents(connection)
        self._playerName = playerName

    def getBlock(self, *args):
        """Get block (x,y,z) => id:int"""
        return self.conn.sendReceive(b"world.getBlock", _intFloor(args))

    def getBlockWithData(self, *args):
        """Get block with data (x,y,z) => Block"""
        return self.conn.sendReceiveList(b"world.getBlockWithData", _intFloor(args), sep=",")

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
        return self.conn.sendReceive(b"world.isBlockPassable", *args) == "true"

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
        """Get the height of the world (x,z) => int"""
        return int(self.conn.sendReceive(b"world.getHeight", _intFloor(args)))

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
        if self.conn.sendReceive(b"setPlayer", name):
            self._playerName = name
            return True
        else:
            return False

    def getPlayerName(self):
        """Get the name of the previously set / currently attached player => str"""
        if self._playerName:
            return self._playerName
        else:
            p = self.conn.sendReceive(b"getPlayer")
            return None if p == "(none)" else p

    playerName = property(getPlayerName)

    @staticmethod
    def create(address="localhost", port=4711, playerName=[], debug=False):
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
