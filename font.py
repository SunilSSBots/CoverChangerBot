# Join Our Telegram Channel :- @SSBotsUpdates
# Subscribe YouTube Channel For More Bots Updates :- SunilWebTricks
# Ask Doubt Contact Me On telegram @Sunil_Sharma_2_0_Bot

"""
Caption Font Styling Engine for Video Cover Bot
Provides Unicode font transformations for captions while preserving URLs, tags and mentions.
"""

import re

# Font transformation character maps
FONT_MAPS = {
    # 1. Bold Sans (Math Sans Bold)
    "bold": {
        "A": "𝗔", "B": "𝗕", "C": "𝗖", "D": "𝗗", "E": "𝗘", "F": "𝗙", "G": "𝗚", "H": "𝗛",
        "I": "𝗜", "J": "𝗝", "K": "𝗞", "L": "𝗟", "M": "𝗠", "N": "𝗡", "O": "𝗢", "P": "𝗣",
        "Q": "𝗤", "R": "𝗥", "S": "𝗦", "T": "𝗧", "U": "𝗨", "V": "𝗩", "W": "𝗪", "X": "𝗫",
        "Y": "𝗬", "Z": "𝗭",
        "a": "𝗮", "b": "𝗯", "c": "𝗰", "d": "𝗱", "e": "𝗲", "f": "𝗳", "g": "𝗴", "h": "𝗵",
        "i": "𝗶", "j": "𝗷", "k": "𝗸", "l": "𝗹", "m": "𝗺", "n": "𝗻", "o": "𝗼", "p": "𝗽",
        "q": "𝗾", "r": "𝗿", "s": "𝘀", "t": "𝘁", "u": "𝘂", "v": "𝘃", "w": "𝘄", "x": "𝘅",
        "y": "𝘆", "z": "𝘇",
        "0": "𝟬", "1": "𝟭", "2": "𝟮", "3": "𝟯", "4": "𝟰", "5": "𝟱", "6": "𝟲", "7": "𝟳",
        "8": "𝟴", "9": "𝟵"
    },
    
    # 2. Bold Serif
    "bold_serif": {
        "A": "𝐀", "B": "𝐁", "C": "𝐂", "D": "𝐃", "E": "𝐄", "F": "𝐅", "G": "𝐆", "H": "𝐇",
        "I": "𝐈", "J": "𝐉", "K": "𝐊", "L": "𝐋", "M": "𝐌", "N": "𝐍", "O": "𝐎", "P": "𝐏",
        "Q": "𝐐", "R": "𝐑", "S": "𝐒", "T": "𝐓", "U": "𝐔", "V": "𝐕", "W": "𝐖", "X": "𝐗",
        "Y": "𝐘", "Z": "𝐙",
        "a": "𝐚", "b": "𝐛", "c": "𝐜", "d": "𝐝", "e": "𝐞", "f": "𝐟", "g": "𝐠", "h": "𝐡",
        "i": "𝐢", "j": "𝐣", "k": "𝐤", "l": "𝐥", "m": "𝐦", "n": "𝐧", "o": "𝐨", "p": "𝐩",
        "q": "𝐪", "r": "𝐫", "s": "𝐬", "t": "𝐭", "u": "𝐮", "v": "𝐯", "w": "𝐰", "x": "𝐱",
        "y": "𝐲", "z": "𝐳",
        "0": "𝟎", "1": "𝟏", "2": "𝟐", "3": "𝟑", "4": "𝟒", "5": "𝟓", "6": "𝟔", "7": "𝟕",
        "8": "𝟖", "9": "𝟗"
    },

    # 3. Italic Sans
    "italic": {
        "A": "𝘈", "B": "𝘉", "C": "𝘊", "D": "𝘋", "E": "𝘌", "F": "𝘍", "G": "𝘎", "H": "𝘏",
        "I": "𝘐", "J": "𝘑", "K": "𝘒", "L": "𝘓", "M": "𝘔", "N": "𝘕", "O": "𝘖", "P": "𝘗",
        "Q": "𝘘", "R": "𝘙", "S": "𝘚", "T": "𝘛", "U": "𝘜", "V": "𝘝", "W": "𝘞", "X": "𝘟",
        "Y": "𝘠", "Z": "𝘡",
        "a": "𝘢", "b": "𝘣", "c": "𝘤", "d": "𝘥", "e": "𝘦", "f": "𝘧", "g": "𝘨", "h": "𝘩",
        "i": "𝘪", "j": "𝘫", "k": "𝘬", "l": "𝘭", "m": "𝘮", "n": "𝘯", "o": "𝘰", "p": "𝘱",
        "q": "𝘲", "r": "𝘳", "s": "𝘴", "t": "𝘵", "u": "𝘶", "v": "𝘷", "w": "𝘸", "x": "𝘹",
        "y": "𝘺", "z": "𝘻"
    },

    # 4. Bold Italic Sans
    "bold_italic": {
        "A": "𝘼", "B": "𝘽", "C": "𝘾", "D": "𝘿", "E": "𝙀", "F": "𝙁", "G": "𝙂", "H": "𝙃",
        "I": "𝙄", "J": "𝙅", "K": "𝙆", "L": "𝙇", "M": "𝙈", "N": "𝙉", "O": "𝙊", "P": "𝙋",
        "Q": "𝙌", "R": "𝙍", "S": "𝙎", "T": "𝙏", "U": "𝙐", "V": "𝙑", "W": "𝙒", "X": "𝙓",
        "Y": "𝙔", "Z": "𝙕",
        "a": "𝙖", "b": "𝙗", "c": "𝙘", "d": "𝙙", "e": "𝙚", "f": "𝙛", "g": "𝙜", "h": "𝙝",
        "i": "𝙞", "j": "𝙟", "k": "𝙠", "l": "𝙡", "m": "𝙢", "n": "𝙣", "o": "𝙤", "p": "𝙥",
        "q": "𝙦", "r": "𝙧", "s": "𝙨", "t": "𝙩", "u": "𝙪", "v": "𝙫", "w": "𝙬", "x": "𝙭",
        "y": "𝙮", "z": "𝙯"
    },

    # 5. Monospace
    "mono": {
        "A": "𝙰", "B": "𝙱", "C": "𝙲", "D": "𝙳", "E": "𝙴", "F": "𝙵", "G": "𝙶", "H": "𝙷",
        "I": "𝙸", "J": "𝙹", "K": "𝙺", "L": "𝙻", "M": "𝙼", "N": "𝙽", "O": "𝙾", "P": "𝙿",
        "Q": "𝚀", "R": "𝚁", "S": "𝚂", "T": "𝚃", "U": "𝚄", "V": "𝚅", "W": "𝚆", "X": "𝚇",
        "Y": "𝚈", "Z": "𝚉",
        "a": "𝚊", "b": "𝚋", "c": "𝚌", "d": "𝚍", "e": "𝚎", "f": "𝚏", "g": "𝚐", "h": "𝚑",
        "i": "𝚒", "j": "𝚓", "k": "𝚔", "l": "𝚕", "m": "𝚖", "n": "𝚗", "o": "𝚘", "p": "𝚙",
        "q": "𝚚", "r": "𝚛", "s": "𝚜", "t": "𝚝", "u": "𝚞", "v": "𝚟", "w": "𝚠", "x": "𝚡",
        "y": "𝚢", "z": "𝚣",
        "0": "𝟶", "1": "𝟷", "2": "𝟸", "3": "𝟹", "4": "𝟺", "5": "𝟻", "6": "𝟼", "7": "𝟽",
        "8": "𝟾", "9": "𝟿"
    },

    # 6. Small Caps
    "small_caps": {
        "A": "ᴀ", "B": "ʙ", "C": "ᴄ", "D": "ᴅ", "E": "ᴇ", "F": "ꜰ", "G": "ɢ", "H": "ʜ",
        "I": "ɪ", "J": "ᴊ", "K": "ᴋ", "L": "ʟ", "M": "ᴍ", "N": "ɴ", "O": "ᴏ", "P": "ᴘ",
        "Q": "ǫ", "R": "ʀ", "S": "s", "T": "ᴛ", "U": "ᴜ", "V": "ᴠ", "W": "ᴡ", "X": "x",
        "Y": "ʏ", "Z": "ᴢ",
        "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ", "h": "ʜ",
        "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ", "o": "ᴏ", "p": "ᴘ",
        "q": "ǫ", "r": "ʀ", "s": "s", "t": "ᴛ", "u": "ᴜ", "v": "ᴠ", "w": "ᴡ", "x": "x",
        "y": "ʏ", "z": "ᴢ"
    },

    # Title Serif + Small Caps (e.g. 𝐀ᴅᴅ 𝐌ᴇ 𝐓ᴏ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ)
    "title_serif_caps": {
        "A": "𝐀", "B": "𝐁", "C": "𝐂", "D": "𝐃", "E": "𝐄", "F": "𝐅", "G": "𝐆", "H": "𝐇",
        "I": "𝐈", "J": "𝐉", "K": "𝐊", "L": "𝐋", "M": "𝐌", "N": "𝐍", "O": "𝐎", "P": "𝐏",
        "Q": "𝐐", "R": "𝐑", "S": "𝐒", "T": "𝐓", "U": "𝐔", "V": "𝐕", "W": "𝐖", "X": "𝐗",
        "Y": "𝐘", "Z": "𝐙",
        "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ", "h": "ʜ",
        "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ", "o": "ᴏ", "p": "ᴘ",
        "q": "ǫ", "r": "ʀ", "s": "s", "t": "ᴛ", "u": "ᴜ", "v": "ᴠ", "w": "ᴡ", "x": "x",
        "y": "ʏ", "z": "ᴢ",
        "0": "𝟎", "1": "𝟏", "2": "𝟐", "3": "𝟑", "4": "𝟒", "5": "𝟓", "6": "𝟔", "7": "𝟕",
        "8": "𝟖", "9": "𝟗"
    },

    # 7. Cursive / Script
    "script": {
        "A": "𝒜", "B": "𝐵", "C": "𝒞", "D": "𝒟", "E": "𝐸", "F": "𝐹", "G": "𝒢", "H": "𝐻",
        "I": "𝐼", "J": "𝒥", "K": "𝒦", "L": "𝐿", "M": "𝑀", "N": "𝒩", "O": "𝒪", "P": "𝒫",
        "Q": "𝒬", "R": "𝑅", "S": "𝒮", "T": "𝒯", "U": "𝒰", "V": "𝒱", "W": "𝒲", "X": "𝒳",
        "Y": "𝒴", "Z": "𝒵",
        "a": "𝒶", "b": "𝒷", "c": "𝒸", "d": "𝒹", "e": "𝑒", "f": "𝒻", "g": "𝑔", "h": "𝒽",
        "i": "𝒾", "j": "𝒿", "k": "𝓀", "l": "𝓁", "m": "𝓂", "n": "𝓃", "o": "𝑜", "p": "𝓅",
        "q": "𝓆", "r": "𝓇", "s": "𝓈", "t": "𝓉", "u": "𝓊", "v": "𝓋", "w": "𝓌", "x": "𝓍",
        "y": "𝓎", "z": "𝓏"
    },

    # 8. Bold Script
    "bold_script": {
        "A": "𝓐", "B": "𝓑", "C": "𝓒", "D": "𝓓", "E": "𝓔", "F": "𝓕", "G": "𝓖", "H": "𝓗",
        "I": "𝓘", "J": "𝓙", "K": "𝓚", "L": "𝓛", "M": "𝓜", "N": "𝓝", "O": "𝓞", "P": "𝓟",
        "Q": "𝓠", "R": "𝓡", "S": "𝓢", "T": "𝓣", "U": "𝓤", "V": "𝓥", "W": "𝓦", "X": "𝓧",
        "Y": "𝓨", "Z": "𝓩",
        "a": "𝓪", "b": "𝓫", "c": "𝓬", "d": "𝓭", "e": "𝓮", "f": "𝓯", "g": "𝓰", "h": "𝓱",
        "i": "𝓲", "j": "𝓳", "k": "𝓴", "l": "𝓵", "m": "𝓶", "n": "𝓷", "o": "𝓸", "p": "𝓹",
        "q": "𝓺", "r": "𝓻", "s": "𝓼", "t": "𝓽", "u": "𝓾", "v": "𝓿", "w": "𝔀", "x": "𝔁",
        "y": "𝔂", "z": "𝔃"
    },

    # 9. Gothic / Fraktur
    "gothic": {
        "A": "𝔄", "B": "𝔅", "C": "ℭ", "D": "𝔇", "E": "𝔈", "F": "𝔉", "G": "𝔊", "H": "ℌ",
        "I": "ℑ", "J": "𝔍", "K": "𝔎", "L": "𝔏", "M": "𝔐", "N": "𝔑", "O": "𝔒", "P": "𝔓",
        "Q": "𝔔", "R": "ℜ", "S": "𝔖", "T": "𝔗", "U": "𝔘", "V": "𝔙", "W": "𝔚", "X": "𝔛",
        "Y": "𝔜", "Z": "ℨ",
        "a": "𝔞", "b": "𝔟", "c": "𝔠", "d": "𝔡", "e": "𝔢", "f": "𝔣", "g": "𝔤", "h": "𝔥",
        "i": "𝔦", "j": "𝔧", "k": "𝔨", "l": "𝔩", "m": "𝔪", "n": "𝔫", "o": "𝔬", "p": "𝔭",
        "q": "𝔮", "r": "𝔯", "s": "𝔰", "t": "𝔱", "u": "𝔲", "v": "𝔳", "w": "𝔴", "x": "𝔵",
        "y": "𝔶", "z": "𝔷"
    },

    # 10. Double Struck / Blackboard Bold
    "double_struck": {
        "A": "𝔸", "B": "𝔹", "C": "ℂ", "D": "𝔻", "E": "𝔼", "F": "𝔽", "G": "𝔾", "H": "ℍ",
        "I": "𝕀", "J": "𝕁", "K": "𝕂", "L": "𝕃", "M": "𝕄", "N": "ℕ", "O": "𝕆", "P": "ℙ",
        "Q": "ℚ", "R": "ℝ", "S": "𝕊", "T": "𝕋", "U": "𝕌", "V": "𝕍", "W": "𝕎", "X": "𝕏",
        "Y": "𝕐", "Z": "ℤ",
        "a": "𝕒", "b": "𝕓", "c": "𝕔", "d": "𝕕", "e": "𝕖", "f": "𝕗", "g": "𝕘", "h": "𝕙",
        "i": "𝕚", "j": "𝕛", "k": "𝕜", "l": "𝕝", "m": "𝕞", "n": "𝕟", "o": "𝕠", "p": "𝕡",
        "q": "𝕢", "r": "𝕣", "s": "𝕤", "t": "𝕥", "u": "𝕦", "v": "𝕧", "w": "𝕨", "x": "𝕩",
        "y": "𝕪", "z": "𝕫",
        "0": "𝟘", "1": "𝟙", "2": "𝟚", "3": "𝟛", "4": "𝟜", "5": "𝟝", "6": "𝟞", "7": "𝟟",
        "8": "𝟠", "9": "𝟡"
    },

    # 11. Circled / Bubble
    "circled": {
        "A": "Ⓐ", "B": "Ⓑ", "C": "Ⓒ", "D": "Ⓓ", "E": "Ⓔ", "F": "Ⓕ", "G": "Ⓖ", "H": "Ⓗ",
        "I": "Ⓘ", "J": "Ⓙ", "K": "Ⓚ", "L": "Ⓛ", "M": "Ⓜ", "N": "Ⓝ", "O": "Ⓞ", "P": "Ⓟ",
        "Q": "Ⓠ", "R": "Ⓡ", "S": "Ⓢ", "T": "Ⓣ", "U": "Ⓤ", "V": "Ⓥ", "W": "Ⓦ", "X": "Ⓧ",
        "Y": "Ⓨ", "Z": "Ⓩ",
        "a": "ⓐ", "b": "ⓑ", "c": "ⓒ", "d": "ⓓ", "e": "ⓔ", "f": "ⓕ", "g": "ⓖ", "h": "ⓗ",
        "i": "ⓘ", "j": "ⓙ", "k": "ⓚ", "l": "ⓛ", "m": "ⓜ", "n": "ⓝ", "o": "ⓞ", "p": "ⓟ",
        "q": "ⓠ", "r": "ⓡ", "s": "ⓢ", "t": "ⓣ", "u": "ⓤ", "v": "ⓥ", "w": "ⓦ", "x": "ⓧ",
        "y": "ⓨ", "z": "ⓩ",
        "0": "⓪", "1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤", "6": "⑥", "7": "⑦",
        "8": "⑧", "9": "⑨"
    },

    # 12. Dark Boxed / Inverted Circled
    "boxed": {
        "A": "🅐", "B": "🅑", "C": "🅒", "D": "🅓", "E": "🅔", "F": "🅕", "G": "🅖", "H": "🅗",
        "I": "🅘", "J": "🅙", "K": "🅚", "L": "🅛", "M": "🅜", "N": "🅝", "O": "🅞", "P": "🅟",
        "Q": "🅠", "R": "🅡", "S": "🅢", "T": "🅣", "U": "🅤", "V": "🅥", "W": "🅦", "X": "🅧",
        "Y": "🅨", "Z": "🅩",
        "a": "🅐", "b": "🅑", "c": "🅒", "d": "🅓", "e": "🅔", "f": "🅕", "g": "🅖", "h": "🅗",
        "i": "🅘", "j": "🅙", "k": "🅚", "l": "🅛", "m": "🅜", "n": "🅝", "o": "🅞", "p": "🅟",
        "q": "🅠", "r": "🅡", "s": "🅢", "t": "🅣", "u": "🅤", "v": "🅥", "w": "🅦", "x": "🅧",
        "y": "🅨", "z": "🅩",
        "0": "⓿", "1": "➊", "2": "➋", "3": "➌", "4": "➍", "5": "➎", "6": "➏", "7": "➐",
        "8": "➑", "9": "➒"
    },

    # 13. Fullwidth / Typewriter
    "fullwidth": {
        "A": "Ａ", "B": "Ｂ", "C": "Ｃ", "D": "Ｄ", "E": "Ｅ", "F": "Ｆ", "G": "Ｇ", "H": "Ｈ",
        "I": "Ｉ", "J": "Ｊ", "K": "Ｋ", "L": "Ｌ", "M": "Ｍ", "N": "Ｎ", "O": "Ｏ", "P": "Ｐ",
        "Q": "Ｑ", "R": "Ｒ", "S": "Ｓ", "T": "Ｔ", "U": "Ｕ", "V": "Ｖ", "W": "Ｗ", "X": "Ｘ",
        "Y": "Ｙ", "Z": "Ｚ",
        "a": "ａ", "b": "ｂ", "c": "ｃ", "d": "ｄ", "e": "ｅ", "f": "ｆ", "g": "ｇ", "h": "ｈ",
        "i": "ｉ", "j": "ｊ", "k": "ｋ", "l": "ｌ", "m": "ｍ", "n": "ｎ", "o": "ｏ", "p": "ｐ",
        "q": "ｑ", "r": "ｒ", "s": "ｓ", "t": "ｔ", "u": "ｕ", "v": "ｖ", "w": "ｗ", "x": "ｘ",
        "y": "ｙ", "z": "ｚ",
        "0": "０", "1": "１", "2": "２", "3": "３", "4": "４", "5": "５", "6": "６", "7": "７",
        "8": "８", "9": "９"
    }
}

# Style metadata for UI buttons and menus
FONT_STYLES = [
    {"key": "title_serif_caps", "name": "𝐓ɪᴛʟᴇ 𝐒ᴇʀɪꜰ", "preview": "𝐓ɪᴛʟᴇ 𝐒ᴇʀɪꜰ 𝐓ᴇxᴛ"},
    {"key": "bold", "name": "𝗕𝗼𝗹𝗱 𝗦𝗮𝗻𝘀", "preview": "𝗕𝗼𝗹𝗱 𝗧𝗲𝘅𝘁"},
    {"key": "small_caps", "name": "sᴍᴀʟʟ ᴄᴀᴘs", "preview": "sᴍᴀʟʟ ᴄᴀᴘs"},
    {"key": "italic", "name": "𝘐𝘵𝘢𝘭𝘪𝘤 𝘚𝘢𝘯𝘴", "preview": "𝘐𝘵𝘢𝘭𝘪𝘤 𝘛ᴇ𝘹ᴛ"},
    {"key": "bold_italic", "name": "𝘽𝙤𝙡𝙙 𝙄𝙩𝙖𝙡𝙞𝙘", "preview": "𝘽𝙤𝙡𝙙 𝙄𝙩𝙖𝙡𝙞𝙘"},
    {"key": "mono", "name": "𝚖𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎", "preview": "𝚖𝚘𝚗𝚘 𝚝𝚎𝚡𝚝"},
    {"key": "bold_serif", "name": "𝐁𝐨𝐥𝐝 𝐒𝐞𝐫𝐢𝐟", "preview": "𝐁𝐨𝐥𝐝 𝐒𝐞𝐫𝐢𝐟"},
    {"key": "script", "name": "𝒮𝒸𝓇𝒾𝓅𝓉", "preview": "𝒮𝒸𝓇𝒾𝓅𝓉 𝒯𝑒𝓍𝓉"},
    {"key": "bold_script", "name": "𝓑𝓸𝓵𝓭 𝓢𝓬𝓻𝓲𝓹𝓽", "preview": "𝓑𝓸𝓵𝓭 𝓢𝓬𝓻𝓲𝓹𝓽"},
    {"key": "gothic", "name": "𝔊𝔬𝔱𝔥𝔦𝔠", "preview": "𝔊𝔬𝔱𝔥𝔦𝔠 𝔗𝔢𝔵𝔱"},
    {"key": "double_struck", "name": "𝔻𝕠𝕦𝕓𝕝𝕖", "preview": "𝔻𝕠𝕦𝕓𝕝𝕖 𝕋𝕖𝕩𝕥"},
    {"key": "circled", "name": "Ⓒⓘⓡⓒⓛⓔⓓ", "preview": "Ⓒⓘⓡⓒⓛⓔⓓ"},
    {"key": "boxed", "name": "🅑🅞🅧🅔🅓", "preview": "🅑🅞🅧🅔🅓"},
    {"key": "fullwidth", "name": "Ｆｕｌｌｗｉｄｔｈ", "preview": "Ｆｕｌｌｗｉｄｔｈ"},
    {"key": "default", "name": "Normal (Default)", "preview": "Plain Text"}
]


def to_custom_font(text: str) -> str:
    """
    Format standard UI text to Title Serif + Small Caps style:
    e.g. 'Add Me To Your Group & Watch Magic Happen' -> '𝐀ᴅᴅ 𝐌ᴇ 𝐓ᴏ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ & 𝐖ᴀᴛᴄʜ 𝐌ᴀɢɪᴄ 𝐇ᴀᴘᴘᴇɴ'
    Preserves HTML tags like <b>, </b>, <code>, </code>, <i>, </i>, etc.
    """
    if not text:
        return ""
    char_map = FONT_MAPS["title_serif_caps"]
    # Split preserving HTML tags and URLs/mentions
    parts = re.split(r'(<[^>]+>|https?://\S+|t\.me/\S+|@\w+)', text)
    result = []
    for part in parts:
        if not part:
            continue
        if part.startswith("<") and part.endswith(">"):
            result.append(part)
        elif part.startswith("http") or part.startswith("t.me/") or part.startswith("@"):
            result.append(part)
        else:
            result.append("".join(char_map.get(c, c) for c in part))
    return "".join(result)


def transform_word(word: str, font_key: str) -> str:
    """Transform a single word into the target font style if applicable"""
    if font_key == "default" or font_key not in FONT_MAPS:
        return word
    
    char_map = FONT_MAPS[font_key]
    return "".join(char_map.get(ch, ch) for ch in word)


def format_caption(text: str, font_key: str = "bold") -> str:
    """
    Format full caption text with chosen font style.
    Preserves:
      - URLs (https://..., http://..., t.me/...)
      - Telegram Mentions (@username)
      - Hashtags (#tag)
    """
    if not text:
        return ""
    
    if font_key == "default" or font_key not in FONT_MAPS:
        return text
    
    char_map = FONT_MAPS[font_key]
    
    # Tokenize by URLs, mentions, hashtags, and regular text
    pattern = re.compile(r'(https?://\S+|t\.me/\S+|@\w+|#\w+)')
    parts = pattern.split(text)
    
    transformed_parts = []
    for part in parts:
        if not part:
            continue
        # Keep URLs, Telegram links, mentions and hashtags unchanged
        if (part.startswith('http://') or part.startswith('https://') or 
            part.startswith('t.me/') or part.startswith('@') or part.startswith('#')):
            transformed_parts.append(part)
        else:
            # Transform normal text characters
            transformed_parts.append("".join(char_map.get(ch, ch) for ch in part))
            
    return "".join(transformed_parts)


def get_font_name(font_key: str) -> str:
    """Get display name of font style"""
    for style in FONT_STYLES:
        if style["key"] == font_key:
            return style["name"]
    return "𝗕𝗼𝗹𝗱 𝗦𝗮𝗻𝘀"
