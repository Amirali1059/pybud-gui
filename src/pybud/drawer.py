from typing import SupportsIndex, overload

import pybud.ansi as ansi
from pybud.ansi import CR, AnsiColor, ColorType

write_to_file = False

if write_to_file:
    f = open("output.ansi", "w", encoding="utf-8")
    ansi.write = lambda x: f.write(x)
    ansi.writeln = lambda x: f.write(x + "\n")
    ansi.flush = lambda: f.flush()

# ansilen = lambda x: len(ansi.remove_ansi(x))

def get_rgb_if_exists(color: AnsiColor = None):
    return color.rgb if color is not None else None

class ColoredString():
    def __init__(self, string: str, forecolor: tuple[int, int, int] = None, backcolor: tuple[int, int, int] = None, ctype: ColorType = ColorType.LEGACY):
        self.forecolor = AnsiColor(
            rgb=forecolor) if forecolor is not None else None
        self.backcolor = AnsiColor(
            rgb=backcolor, foreground=False) if backcolor is not None else None
        self.str = string
        self.ctype = ctype

    def __len__(self) -> int:
        return len(self.str)

    def tostring(self, ctype: ColorType = None, ignore_background: bool = False):
        __ctype = ctype if ctype is not None else self.ctype
        color = ""
        
        if (not ignore_background) and (self.backcolor is not None):
            color += self.backcolor.get(ctype=__ctype)

        if self.forecolor is not None:
            color += self.forecolor.get(ctype=__ctype)

        return (color + self.str + CR)

    def __str__(self) -> str:
        return self.tostring(self.ctype)

    def __add__(self, other):
        if isinstance(other, str):
            other_ = ColoredString(other)
            return self + other_

        if isinstance(other, ColoredStringList):
            return ColoredStringList.__add__(ColoredStringList([self]), other)

        if self.forecolor == other.forecolor and self.backcolor == other.backcolor:
            return ColoredString(
                string=self.str + other.str,
                forecolor=get_rgb_if_exists(self.forecolor),
                backcolor=get_rgb_if_exists(self.backcolor)
            )
        else:
            return ColoredStringList([self, other])

    def __mul__ (self, other):
        if isinstance(other, int):
            return ColoredString(
                string=self.str * other,
                forecolor=get_rgb_if_exists(self.forecolor),
                backcolor=get_rgb_if_exists(self.backcolor)
            )
        else:
            raise NotImplementedError()

    def __iadd__(self, other):
        return self + other

    @overload
    def __getitem__(self, __p: SupportsIndex): ...

    @overload
    def __getitem__(self, __s: slice): ...

    def __getitem__(self, __p):
        if isinstance(__p, SupportsIndex):
            return ColoredString(
                string=self.str[__p],
                forecolor=get_rgb_if_exists(self.forecolor),
                backcolor=get_rgb_if_exists(self.backcolor)
            )
        elif isinstance(__p, slice):
            return ColoredString(
                string=self.str[__p.start:__p.stop:__p.step],
                forecolor=get_rgb_if_exists(self.forecolor),
                backcolor=get_rgb_if_exists(self.backcolor)
            )

    @overload
    def __setitem__(self, __p: SupportsIndex, __o): ...

    @overload
    def __setitem__(self, __p: slice, __o): ...

    # @overload
    def __setitem__(self, __p, __o):
        if isinstance(__p, SupportsIndex):
            if isinstance(__o, str):
                self.str[__p] = __o
            elif isinstance(__o, ColoredString):
                if len(__o.str) != 1:
                    raise ValueError("Shape mismatch! can not set an index of ColoredString to multiple characters.")
                else:
                    if self.forecolor == __o.forecolor and self.backcolor == __o.backcolor:
                        self.str[__p] = __o.str
                    elif len(self.str) == 1:
                        self.str = __o.str
                    else:
                        raise NotImplementedError("Setting an index of a `ColoredString` to another color is not supported!")
        elif isinstance(__p, slice):
            # the code below is comented because if there's a shape mismatch, this
            # will raise a ValueError for setting self.str anyways...
            # if len(__o.str) != len(self.strp[__p.start:__p.stop:__p.step]):
            #    raise ValueError("Shape mismatch! make sure to set to correct lenght.")

            if isinstance(__o, str):
                self.str[__p.start:__p.stop:__p.step] = __o
            elif isinstance(__o, ColoredString):
                if self.forecolor == __o.forecolor and self.backcolor == __o.backcolor:
                    self.str[__p.start:__p.stop:__p.step] = __o
                elif len(self.str) == len(__o.str):
                    self.str = __o.str
                else:
                    assert __p.step == 1, "step is not supported when differentiating colors!"
                    if self.str[:__p.start] != "":
                        cstr_pre = ColoredString(
                            string=self.str[:__p.start],
                            forecolor=get_rgb_if_exists(self.forecolor),
                            backcolor=get_rgb_if_exists(self.backcolor)
                        )
                    else:
                        cstr_pre = None
                    cstr_center = ColoredString(
                        string=__o.str,
                        forecolor=get_rgb_if_exists(__o.forecolor),
                        backcolor=get_rgb_if_exists(__o.backcolor)
                    )
                    if self.str[__p.stop+len(__o.str):] != "":
                        cstr_post = ColoredString(
                            string=self.str[__p.stop+len(__o.str):],
                            forecolor=get_rgb_if_exists(self.forecolor),
                            backcolor=get_rgb_if_exists(self.backcolor)
                        )
                    else:
                        cstr_post = None

                    # return the simplest representation
                    if cstr_post is None and cstr_pre is None:
                        return cstr_center
                    elif cstr_post is None:
                        return ColoredStringList([cstr_pre, cstr_center])
                    elif cstr_pre is None:
                        return ColoredStringList([cstr_center, cstr_post])
                    else:
                        return ColoredStringList([cstr_pre, cstr_center, cstr_post])

    @overload
    def __delitem__(self, __i: SupportsIndex): ...

    @overload
    def __delitem__(self, __s: slice): ...

    def __delitem__(self, __p):
        if isinstance(__p, SupportsIndex):
            del self.str[__p]
        elif isinstance(__p, slice):
            del self.str[__p.start:__p.stop:__p.step]

    # def __add__(self, other:str):
    #    if self.forecolor == None and self.backcolor == None:
    #        return self.str + other
    #    else:
    #        other_ = ColoredString(string=self.str + other)
    #        return ColoredStringList([self, other_])
    def __iadd__(self, other):
        return self + other

# modify built-in string class
# from forbiddenfruit import curse

# def curse_str():
#    def __add__(self, other: ColoredString):
#        if isinstance(other, ColoredString):
#            return ColoredString(self) + other
#        elif isinstance(other, ColoredStringList):
#            return ColoredString(self) + other
#        else:
#            return super(str, self).__add__(other)
#    curse(str, "__add__", __add__)
# curse_str()

class ColoredStringList():
    def __init__(self, strings: ColoredString, ctype: ColorType = ColorType.LEGACY):
        self.strs: list[ColoredString] = strings
        self.ctype = ctype

    def copy(self):
        return ColoredStringList(list(self.strs))

    def tostring(self, ctype: ColorType = None, ignore_background: bool = False):
        result = ""
        fc_c = None
        bc_c = None
        for cstr in self.strs:
            fc_now = cstr.forecolor
            bc_now = cstr.backcolor

            if fc_now != fc_c:
                if fc_now is not None:
                    result += fc_now.get(ctype)
                else:
                    result += ansi.ForeColors.Default
                fc_c = fc_now

            if (not ignore_background) and (bc_now != bc_c):
                if bc_now is not None:
                    result += bc_now.get(ctype)
                else:
                    result += ansi.BackColors.Default
                fc_c = fc_now

            result += cstr.str
        return result.replace("\n", ansi.CR + "\n")

    def __str__(self) -> str:
        return self.tostring(self.ctype)

    def __len__(self) -> int:
        return sum(map(len, self.strs))

    @overload
    def __add__(self, other: 'ColoredStringList'): ...

    @overload
    def __add__(self, other: ColoredString): ...

    @overload
    def __add__(self, other: str): ...

    def __add__(self, other):
        if isinstance(other, ColoredStringList):
            return ColoredStringList(self.strs + other.strs)
        elif isinstance(other, ColoredString):
            # return ColoredStringList(self.strs + [other]) (is not optimized)

            # if self.strs[-1] + other can be optimized to a single ColoredString object
            # this will return a ColoredString, else it will return a ColoredStringList
            # the value then will be added to self.strs[:-1]
            new_last = self.strs[-1] + other
            if isinstance(new_last, ColoredString):
                return ColoredStringList(self.strs[:-1] + [new_last])
            elif isinstance(new_last, ColoredStringList):
                return ColoredStringList(self.strs[:-1] + new_last.strs)
        elif isinstance(other, str):
            return self + ColoredString(string=other)
        else:
            raise NotImplementedError(
                f"`ColoredStringList` Only supports to be added to a \"ColoredString\", \"ColoredStringList\" or \"str\", but got \"{type(other)}\"")

    def __iadd__(self, other):
        return self + other

    @overload
    def __getitem__(self, __p: SupportsIndex): ...

    @overload
    def __getitem__(self, __s: slice): ...

    def __getitem__(self, __p):
        if isinstance(__p, SupportsIndex):
            p = 0
            for cstr in self.strs:
                # if cstr is empty continue (this should never happen but we want to be optimized)
                if len(cstr) == 0:
                    continue
                if (__p - p - len(cstr)) < 0:
                    r = cstr[__p-p]
                    return r
                else:
                    p += len(cstr)
            raise IndexError("Index out of range!")
        elif isinstance(__p, slice):
            # TODO: optimize this
            st = 0 if __p.start is None else __p.start
            et = len(self) if __p.stop is None else __p.stop
            s = 1 if __p.step is None else __p.step
            r = ColoredString("")
            for i in range(st, et, s):
                r += self[i]
            return r


def assign_to_cstrlist(text: ColoredString, __list: list[ColoredString], __i: SupportsIndex):
    l = __list.copy()

    text_len = len(text)
    idx_c = 0
    text_pos_c = 0
    for i, c in enumerate(l):
        if (idx_c + len(c)) > __i:
            # sel_id = i
            el_len = len(l[i])
            relative_pos = __i-idx_c+text_pos_c
            write_len = min(el_len - relative_pos, text_len-text_pos_c)
            backcolor_overwrite = get_rgb_if_exists(text.backcolor)
            if backcolor_overwrite is None:
                backcolor_overwrite = get_rgb_if_exists(l[i].backcolor)
            text_overwrite = ColoredString(
                string=text[text_pos_c:text_pos_c+write_len].str,
                forecolor=get_rgb_if_exists(text.forecolor),
                backcolor=backcolor_overwrite
            )
            if write_len == el_len:
                l[i] = text_overwrite
            else:
                l[i] = [l[i][:relative_pos], text_overwrite,
                        l[i][relative_pos+write_len:]]
            if ((text_pos_c+write_len) >= text_len):
                break
            text_pos_c += write_len
        idx_c += len(c)
    l_out = []
    for el in l:
        if isinstance(el, list):
            l_out += [__el for __el in el if __el != ""]
        else:
            l_out.append(el)
    return l_out


def write_to_cstrlist(text: str, __list: list[ColoredString], __i: SupportsIndex):
    l = __list.copy()
    text_len = len(text)
    idx_c = 0
    text_pos_c = 0
    for i, c in enumerate(l):
        if (idx_c + len(c)) > __i:
            # sel_id = i
            el_len = len(l[i])
            relative_pos = __i-idx_c+text_pos_c
            write_len = min(el_len - relative_pos, text_len-text_pos_c)
            text_overwrite = ColoredString(
                string=text[text_pos_c:text_pos_c+write_len],
                backcolor=l[i].backcolor.rgb if l[i].backcolor else None
            )
            if write_len == el_len:
                l[i] = text_overwrite
            else:
                l[i] = [l[i][:relative_pos], text_overwrite,
                        l[i][relative_pos+write_len:]]
            if ((text_pos_c+write_len) >= text_len):
                break
            text_pos_c += write_len
        idx_c += len(c)
    l_out = []
    for el in l:
        if isinstance(el, list):
            l_out += [__el for __el in el if __el != ""]
        else:
            l_out.append(el)
    return l_out


class Drawer(object):
    def __init__(self, size: tuple[int, int], background_color: tuple[int, int, int] = None):
        self.w = size[0]
        self.h = size[1]

        self.plane: list = [ColoredString(
            " " * self.w, backcolor=background_color) for i in range(self.h)]

    def __str__(self):
        return self.tostring()

    def tostring(self, ctype: ColorType = None, ignore_background: bool = False):
        result = ColoredString("")
        for i, line in enumerate(self.plane):
            if (i < (len(self.plane)-1)):
                result += line + "\n"
            else:
                result += line
        return result.tostring(ctype, ignore_background) + CR

    def write_text(self, text: str, pos: list[int, int], color: list[int, int, int] = None):
        assert isinstance(text, str)
        idx = pos[0]
        ln_idx = pos[1]

        if (idx >= self.w):
            return
        if (ln_idx < 0 or ln_idx >= self.h):
            return

        # fix text clipping out of frame
        if (idx < 0):
            text = text[-idx:]
            idx = 0
        text = text[:self.w - idx]

        line = self.plane[ln_idx]
        if isinstance(line, ColoredString):
            line_new = line[:idx] + ColoredString(
                string=text,
                forecolor=color,
                backcolor=get_rgb_if_exists(line.backcolor)
            ) + line[idx+len(text):]
            self.plane[ln_idx] = line_new
        elif isinstance(line, ColoredStringList):
            new_strs = write_to_cstrlist(text, line.strs, idx)
            new_line = ColoredStringList(new_strs)
            self.plane[ln_idx] = new_line

    def place(self, text, pos: list[int, int]):
        idx = pos[0]
        ln_idx = pos[1]
        if (idx >= self.w):
            return
        if (ln_idx < 0 or ln_idx >= self.h):
            return
        line = self.plane[ln_idx]
        if isinstance(text, ColoredStringList):
            idx_c = idx
            for cstr in text.strs:
                self.place(cstr, (idx_c, ln_idx))
                idx_c += len(cstr)
            return
        if len(text) == 0:
            return

        # fix text clipping out of frame
        if (idx < 0):
            text = text[-idx:]
            idx = 0
        text = text[:self.w - idx]
    
        if isinstance(line, ColoredString):
            backcolor_overwrite = get_rgb_if_exists(text.backcolor)
            if backcolor_overwrite is None:
                backcolor_overwrite = get_rgb_if_exists(line.backcolor)
            new_line = line[:idx] + ColoredString(
                string=text.str,
                forecolor=get_rgb_if_exists(text.forecolor),
                backcolor=backcolor_overwrite
            ) + line[idx+len(text):]
            self.plane[ln_idx] = new_line
        elif isinstance(line, ColoredStringList):
            new_strs = assign_to_cstrlist(text, line.strs, idx)
            new_line = ColoredStringList(new_strs)
            self.plane[ln_idx] = new_line

    def center_write(self, text, ln_idx: int):
        idx = (self.w - len(text))//2
        self.write_text(text, pos=(ln_idx, idx))

    def center_place(self, text, ln_idx: int):
        idx = (self.w - len(text))//2
        self.place(text, pos=(idx, ln_idx))
    
    def place_drawer(self, other_drawer: 'Drawer', pos: list[int, int], borderless: bool = True, shadow: bool = False):
        idx = pos[0]
        ln_idx = pos[1]
        if (idx >= self.w):
            return
        if (ln_idx < 0 or ln_idx >= self.h):
            return
        
        if not borderless:
            # shadow character
            sc = ColoredString("\\", forecolor=(180, 180, 180)) if shadow else ColoredString(" ")
            # place window with border
            self.place(ColoredString("┌") + ColoredString("─" * other_drawer.w) + ColoredString("┐"), (idx-1, ln_idx - 1))
            i = 0
            for i, cstr in enumerate(other_drawer.plane):
                self.place(sc + ColoredString("│") + cstr + ColoredString("│"), (idx-2, i + ln_idx))
            self.place(sc + ColoredString("└") + ColoredString("─" * other_drawer.w) + ColoredString("┘"), (idx-2, i + ln_idx + 1))
            self.place(sc * (other_drawer.w + 3), (idx-2, i + ln_idx + 2))
            return
        else:
            for i, cstr in enumerate(other_drawer.plane):
                self.place(cstr, (idx, i + ln_idx))
            return
    
    def center_place_drawer(self, other_drawer: 'Drawer', ln_idx: int, borderless: bool = True):
        idx = (self.w - other_drawer.w)//2
        self.place_drawer(other_drawer, pos=(idx, ln_idx), borderless = borderless)

if __name__ == "__main__":
    #result = "test" + (ColoredString("will this work?") + ColoredString("will this work?", forecolor=(0, 255, 0)))
    #print(result)

    # test = ColoredString("test ", forecolor=(0, 100, 200)) + ColoredString("for ", forecolor=(0, 100, 200)) + ColoredString("colors", forecolor=(0, 100, 200), backcolor=(200, 100, 200))
    tsize = ansi.get_size()
    screen = Drawer(size=(tsize.columns, tsize.lines))
    drawer = Drawer(size=(31, 5))
    drawer.write_text("Hello, World!", ((drawer.w-13)//2, 2))
    # painter.place(ColoredString("Hello, World!", forecolor=(200, 100, 0)), (8, 5))
    welcome_text = ColoredString("-"*((drawer.w-15)//2)+"[", forecolor=(0, 255, 0)) + ColoredString(
        "Welcome", forecolor=(255, 255, 0)) + ColoredString("]"+"-"*((drawer.w-15)//2), forecolor=(0, 255, 0))
    test_text = ColoredString("-"*((drawer.w-15)//2)+"[", forecolor=(0, 255, 0)) + ColoredString(
        "TEST", forecolor=(255, 255, 0)) + ColoredString("]"+"-"*((drawer.w-15)//2), forecolor=(0, 0, 0))
    drawer.center_place(welcome_text, ln_idx=1)
    drawer.place(test_text, pos=(0, 1))
    # print(type(drawer))
    screen.center_place_drawer(drawer, 10, borderless = False)
    ansi.write(screen.tostring(ctype=ColorType.TRUECOLOR))
    ansi.flush()
    input()
