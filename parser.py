#! /usr/bin/env python
"""Playing with hachoir to parse SQLite files
"""

import os
import sqlite3

from hachoir.field import Parser, CString, UInt8, UInt16, UInt32, String, Bytes,RawBytes,FieldSet
from hachoir.stream import StringInputStream, BIG_ENDIAN




class SQLite_page(Parser):
    """
    Offset	Size	Description
        0	1	The one-byte flag at offset 0 indicating the b-tree page type.
                A value of 2 (0x02) means the page is an interior index b-tree page.
                A value of 5 (0x05) means the page is an interior table b-tree page.
                A value of 10 (0x0a) means the page is a leaf index b-tree page.
                A value of 13 (0x0d) means the page is a leaf table b-tree page.
                Any other value for the b-tree page type is an error.
        1	2	The two-byte integer at offset 1 gives the start of the first freeblock on the page, or is zero if there are no freeblocks.
        3	2	The two-byte integer at offset 3 gives the number of cells on the page.
        5	2	The two-byte integer at offset 5 designates the start of the cell content area. A zero value for this integer is interpreted as 65536.
        7	1	The one-byte integer at offset 7 gives the number of fragmented free bytes within the cell content area.
        8	4	The four-byte page number at offset 8 is the right-most pointer. This value appears in the header of interior b-tree pages only and is omitted from all other pages.
    """

    endian = BIG_ENDIAN


    def createFields(self):
        yield UInt8(self, 'PageType')
        yield UInt16(self, 'FirstFree')
        yield UInt16(self, 'CellsNumber')
        yield UInt16(self, 'CellStart')
        yield UInt8(self, 'CellFree')
        if (self['PageType'].value == 5 or self['PageType'].value == 2):
            yield UInt32(self, 'RightPoint')
        for index in range(self["CellsNumber"].value):
            yield UInt16(self, 'CellPoint[]')







class SQLite_page_hand(FieldSet):
    """
    Offset	Size	Description
        0	1	The one-byte flag at offset 0 indicating the b-tree page type.
                A value of 2 (0x02) means the page is an interior index b-tree page.
                A value of 5 (0x05) means the page is an interior table b-tree page.
                A value of 10 (0x0a) means the page is a leaf index b-tree page.
                A value of 13 (0x0d) means the page is a leaf table b-tree page.
                Any other value for the b-tree page type is an error.
        1	2	The two-byte integer at offset 1 gives the start of the first freeblock on the page, or is zero if there are no freeblocks.
        3	2	The two-byte integer at offset 3 gives the number of cells on the page.
        5	2	The two-byte integer at offset 5 designates the start of the cell content area. A zero value for this integer is interpreted as 65536.
        7	1	The one-byte integer at offset 7 gives the number of fragmented free bytes within the cell content area.
        8	4	The four-byte page number at offset 8 is the right-most pointer. This value appears in the header of interior b-tree pages only and is omitted from all other pages.
    """

    endian = BIG_ENDIAN

    def createFields(self):
        yield UInt8(self, 'PageType')
        yield UInt16(self, 'FirstFree')
        yield UInt16(self, 'CellsNumber')
        yield UInt16(self, 'CellStart')
        yield UInt8(self, 'CellFree')
        yield UInt32(self, 'RightPoint')
        for index in range(self["CellsNumber"].value):
            yield UInt16(self, 'CellPoint[]')
        #yield RawBytes(self,)




class SQLite_hand(Parser):
    """
    Offset	Size	Description
    0	16	 The header string: "SQLite format 3\000"
    16	2	 The database page size in bytes. Must be a power of two between 512 and 32768 inclusive, or the value 1 representing a page size of 65536.
    18	1	 File format write version. 1 for legacy; 2 for WAL.
    19	1	 File format read version. 1 for legacy; 2 for WAL.
    20	1	 Bytes of unused "reserved" space at the end of each page. Usually 0.
    21	1	 Maximum embedded payload fraction. Must be 64.
    22	1	 Minimum embedded payload fraction. Must be 32.
    23	1	 Leaf payload fraction. Must be 32.
    24	4	 File change counter.
    28	4	 Size of the database file in pages. The "in-header database size".
    32	4	 Page number of the first freelist trunk page.
    36	4	 Total number of freelist pages.
    40	4	 The schema cookie.
    44	4	 The schema format number. Supported schema formats are 1, 2, 3, and 4.
    48	4	 Default page cache size.
    52	4	 The page number of the largest root b-tree page when in auto-vacuum or incremental-vacuum modes, or zero otherwise.
    56	4	 The database text encoding. A value of 1 means UTF-8. A value of 2 means UTF-16le. A value of 3 means UTF-16be.
    60	4	 The "user version" as read and set by the user_version pragma.
    64	4	 True (non-zero) for incremental-vacuum mode. False (zero) otherwise.
    68	24	 Reserved for expansion. Must be zero.
    92	4	 The version-valid-for number.
    96	4	SQLITE_VERSION_NUMBER
    """

    endian = BIG_ENDIAN

    def createFields(self):
        yield String(self, 'HeaderString', 16)
        yield UInt16(self, 'PageSize')
        yield UInt8(self, 'WriteVersion')
        yield UInt8(self, 'ReadVersion')
        yield UInt8(self, 'ReservedSpace')
        yield UInt8(self, 'MaxEmbeddedPayloadFraction')
        yield UInt8(self, 'MinEmbeddedPayloadFraction')
        yield UInt8(self, 'LeafPayloadFraction')
        yield UInt32(self, 'FileChangeCounter')
        yield UInt32(self, 'SizeInPages')
        yield UInt32(self, 'FirstFreelistPage')
        yield UInt32(self, 'FreelistTotal')
        yield UInt32(self, 'SchemaCookie')
        yield UInt32(self, 'SchemaFormatNumber')
        yield UInt32(self, 'DefaultPageCacheSize')
        yield UInt32(self, 'MagicPageNumber')
        yield UInt32(self, 'TextEncoding')
        yield UInt32(self, 'UserVersion')
        yield UInt32(self, 'IncrementalVacuumMode')
        yield Bytes(self, 'ReservedForExpansion', 24)
        yield UInt32(self, 'VersionValidFor')
        yield UInt32(self, 'SqliteVersion')
        yield SQLite_page_hand(self, 'PageHand')
        # yield RawBytes(self, 'Padding', 3984)


def main(argv):
    DATA_FILE = argv[0]
    file_handle = open(DATA_FILE, 'rb')
    stream = StringInputStream(file_handle.read(4096))
    print("parser No.1 page hand")
    point = SQLite_hand(stream)
    for field in point:
        print("%s) %s=%s" % (field.address, field.name, field.display))
    for k in range(20):
        stream = StringInputStream(file_handle.read(4096))
        print("\nparser No.%d page" % (k+2))
        point = SQLite_page(stream)
        for field in point:
            print("%s) %s=%s" % (field.address, field.name, field.display))





if __name__ == '__main__':
    from sys import argv
    main(argv[1:])


