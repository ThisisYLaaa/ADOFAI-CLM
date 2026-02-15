from dataclasses import dataclass, field
from typing import Any, Dict, List
from src.util.Logger import get_logger

logger = get_logger("数据结构")

@dataclass
class Settings:
    version: int
    artist: str = ""
    specialArtistType: str = "None"
    artistPermission: str = ""
    song: str = ""
    author: str = ""
    separateCountdownTime: bool = True
    previewImage: str = ""
    previewIcon: str = ""
    previewIconColor: str = "003f52"
    previewSongStart: int = 0
    previewSongDuration: int = 10
    seizureWarning: bool = False
    levelDesc: str = ""
    levelTags: str = ""
    artistLinks: str = ""
    speedTrialAim: int = 0
    difficulty: int = 1
    requiredMods: List[str] = field(default_factory=list)
    songFilename: str = ""
    bpm: int = 100
    volume: int = 100
    offset: int = 0
    pitch: int = 100
    hitsound: str = "Kick"
    hitsoundVolume: int = 100
    countdownTicks: int = 4
    songURL: str = ""
    tileShape: str = "Long"
    trackColorType: str = "Single"
    trackColor: str = "debb7b"
    secondaryTrackColor: str = "ffffff"
    trackColorAnimDuration: int = 2
    trackColorPulse: str = "None"
    trackPulseLength: int = 10
    trackStyle: str = "Standard"
    trackTexture: str = ""
    trackTextureScale: int = 1
    trackGlowIntensity: int = 100
    trackAnimation: str = "None"
    beatsAhead: int = 3
    trackDisappearAnimation: str = "None"
    beatsBehind: int = 4
    backgroundColor: str = "000000"
    showDefaultBGIfNoImage: bool = True
    showDefaultBGTile: bool = True
    defaultBGTileColor: str = "101121"
    defaultBGShapeType: str = "Default"
    defaultBGShapeColor: str = "ffffff"
    bgImage: str = ""
    bgImageColor: str = "ffffff"
    parallax: List[int] = field(default_factory=lambda: [100, 100])
    bgDisplayMode: str = "FitToScreen"
    imageSmoothing: bool = True
    lockRot: bool = False
    loopBG: bool = False
    scalingRatio: int = 100
    relativeTo: str = "Player"
    position: List[int] = field(default_factory=lambda: [0, 0])
    rotation: int = 0
    zoom: int = 100
    pulseOnFloor: bool = True
    bgVideo: str = ""
    loopVideo: bool = False
    vidOffset: int = 0
    floorIconOutlines: bool = False
    stickToFloors: bool = True
    planetEase: str = "Linear"
    planetEaseParts: int = 1
    planetEasePartBehavior: str = "Mirror"
    defaultTextColor: str = "ffffff"
    defaultTextShadowColor: str = "00000050"
    congratsText: str = ""
    perfectText: str = ""
    legacyFlash: bool = False
    legacyCamRelativeTo: bool = False
    legacySpriteTiles: bool = False
    legacyTween: bool = False
    disableV15Features: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """从字典创建Settings实例
        :param data: 包含Settings字段的字典
        :return: Settings实例
        """
        # 过滤出已知字段
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)

@dataclass
class Action:
    floor: int
    eventType: str
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理
        确保extra字段为字典类型
        """
        if not isinstance(self.extra, dict):
            self.extra = {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """从字典创建Action实例
        :param data: 包含Action字段的字典
        :return: Action实例
        """
        floor = data.pop('floor')
        eventType = data.pop('eventType')
        return cls(floor=floor, eventType=eventType, extra=data)

@dataclass
class Level:
    """Adofai关卡数据结构"""
    angleData: List[int]
    settings: Settings
    actions: List[Action]
    decorations: List[Dict[str, Any]]

    def __init__(self, adofai_json: Dict[str, Any]):
        """初始化Adofai关卡数据结构
        :param adofai_json: Adofai关卡的JSON数据
        """
        self.angleData = adofai_json.get('angleData', [])
        self.settings = Settings.from_dict(adofai_json.get('settings', {}))
        self.actions = [Action.from_dict(action.copy()) for action in adofai_json.get('actions', [])]
        self.decorations = adofai_json.get('decorations', [])
