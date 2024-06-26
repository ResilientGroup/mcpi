from .vec3 import Vec3

class BlockEvent:
    """An Event related to blocks (e.g. placed, removed, hit)"""
    HIT = 0

    def __init__(self, type, x, y, z, face, entityId):
        self.type = type
        self.pos = Vec3(int(x), int(y), int(z))
        self.face = face
        self.entityId = entityId

    def __repr__(self):
        sType = {
            BlockEvent.HIT: "BlockEvent.HIT"
        }.get(self.type, "???")

        return "BlockEvent(%s, %d, %d, %d, %s, %s)"%(
            sType, self.pos.x, self.pos.y, self.pos.z, self.face, self.entityId)

    @staticmethod
    def Hit(x, y, z, face, entityId):
        return BlockEvent(BlockEvent.HIT, x, y, z, face, entityId)


class ChatEvent:
    """An Event related to chat (e.g. posts)"""
    POST = 0

    def __init__(self, type, name, entityId, message):
        self.type = type
        self.name = name
        self.entityId = entityId
        self.message = message

    def __repr__(self):
        sType = {
            ChatEvent.POST: "ChatEvent.POST"
        }.get(self.type, "???")

        return "ChatEvent(%s, %s:%s, %s)" % (
            sType, self.name, self.entityId, self.message)

    @staticmethod
    def Post(name, entityId, message):
        return ChatEvent(ChatEvent.POST, name, entityId, message)


class ProjectileEvent:
    """An Event related to projectiles (e.g. placed, removed, hit)"""
    HIT = 0

    def __init__(self, type, x, y, z, face, shooterName,victimName):
        self.type = type
        self.pos = Vec3(int(x), int(y), int(z))
        self.face = face
        self.shooterName = shooterName
        self.victimName = victimName

    def __repr__(self):
        sType = {
            ProjectileEvent.HIT: "ProjectileEvent.HIT"
        }.get(self.type, "???")

        return "ProjectileEvent(%s, %d, %d, %d, %s, %s)" % (
            sType, self.pos.x, self.pos.y, self.pos.z, self.shooterName, self.victimName)

    @staticmethod
    def Hit(x, y, z, face, shooterName,victimName):
        return ProjectileEvent(BlockEvent.HIT, x, y, z, face, shooterName,victimName)
