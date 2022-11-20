import struct
from abc import ABCMeta, abstractmethod
from collections import namedtuple
import codecs


class Block:
    __metaclass__ = ABCMeta

    @abstractmethod
    def read_inf(self, *args):
        """Read information from block"""

    @abstractmethod
    def save_inf(self, *args):
        """Save information from block"""


class Superblock(Block):
    """ Superblock class with file system info"""

    def __init__(self, file: str, size: int):
        """Initialize size of superblock and inner info: sizes of block, FAT table and root.
        :argument:
        file -- path to file with info
        size -- size of superblock
        """
        self.size = size
        suber_info = self.read_inf(file)
        self.size_of_block = suber_info[0]
        self.size_of_fat = suber_info[1]
        self.size_of_root = suber_info[2]
        self.save_inf()

    def __str__(self):
        """Return superblock params and info if we call as a string"""
        return f"Superblock size: {self.size}" \
               f"\nFile system information:" \
               f"\n\t- size of block: {self.size_of_block}" \
               f"\n\t- size of FAT table: {self.size_of_fat}" \
               f"\n\t- size of root (number of files the): {self.size_of_root}"

    def __repr__(self):
        """Return superblock params and info if we call it with repr"""
        return f"Superblock size  in decimal: {self.size}" \
               f"\nSize of block in decimal: {self.size_of_block}, " \
               f" size of FAT table in decimal: {self.size_of_fat}, " \
               f" size of root in decimal: {self.size_of_root}"

    def read_inf(self, file: str):
        """ Read info from the doc file, convert it and return as decimal numbers.
        :argument:
        file -- path to file
        :return:
        superblock params -- info from file about file system in decimal numbers
        """
        with open(file, 'rb') as f:
            info = f.read(self.size)
        info = struct.unpack('lll', info)
        superblock_param = []
        for parm in info:
            superblock_param.append(parm)
        return superblock_param

    def save_inf(self):
        """
        Save information to file Superblock.txt
        """
        with open('Superblock.txt', 'w') as f:
            f.write(f"Superblock: {self.size} bytes where:"
                    f"\n\t-Size if block (4 bytes): {self.size_of_block}"
                    f"\n\t-Size of Fat(4 bytes) : {self.size_of_fat}"
                    f"\n\t-Number of Files in root(4 bytes) : {self.size_of_root}")
        print('SuperBlock information saved in Superblock.txt')


class FatBlock(Block):
    def __init__(self, size: int, elem: int, previous: int, file: str):
        self.size = size
        self.elem = elem
        self.fat_table = self.read_inf(file, previous)

    def __str__(self):
        """Return Fat params if we call as a string"""
        return f"FAT size: {self.size} bytes, size of one row 8 bytes (4 and 4)" \
               f"\n FAT content you can see in file FAT.txt"

    def __repr__(self):
        """Return Fat params if we call it with repr"""
        return f"FAT size: {self.size} bytes in decimal, size of one row 8 bytes (4 and 4)" \
               f"\n FAT content:" \
               f"\n {self.fat_table}" \
               f"\n FAT content you can see in file FAT.txt"

    def read_inf(self, file, previous):
        """
        Read info from file, convert it and call save_inf for saving
        :param file:
        :param previous: size of superblock
        :return: fat_table -- fat table content
        """
        fat_binary = []
        fat_table = []
        with open(file, 'rb') as f:
            f.read(previous)
            for _ in range(0, self.size, 8):
                fat_binary.append(f.read(8))
        for note in fat_binary:
            note = struct.unpack('ll', note)
            fat_table.append(note)
        self.save_inf(fat_table)
        return fat_table

    def save_inf(self, fat_table: list):
        """
        Save FAT table to file FAT.txt
        """
        with open('FAT.txt', 'w') as f:
            f.write(f'FAT table ({self.size} bytes) content:')
            for elem in fat_table:
                f.write(f'\n {elem[0]}   {elem[1]}')
        print('Fat table saved in FAT.txt')


class RootBlock(Block):
    def __init__(self, num_of_files: int, name_size: int, first_block_num: int, atr_size: int,
                 previous: int, file: str):
        self.num_of_files = num_of_files
        self.name_size = name_size
        self.first_block_num = first_block_num
        self.atr_size = atr_size
        self.root_files = self.read_inf(previous, file)

    def __str__(self):
        """Return root params if we call as a string"""
        return f"Root size - number of files: {self.num_of_files}" \
               f"\nFiles information:" \
               f"\n\t- size of name of file: {self.name_size}" \
               f"\n\t- size of number of first block in file: {self.first_block_num}" \
               f"\n\t- size of attributes: {self.atr_size}" \
               f"\n Root content you can see in file Root.txt"

    def __repr__(self):
        """Return root params if we call it with repr"""
        return f"Root size  - number of file: {self.num_of_files}" \
               f"Size of name of file in decimal: {self.name_size}, " \
               f" size of number of first block in file table in decimal: {self.first_block_num}, " \
               f" size of attributes in decimal: {self.atr_size}" \
               f"\n Root content:" \
               f"\n {self.root_files}" \
               f"\n Root content you can see in file Root.txt"

    def read_inf(self, previous: int, file: str):
        """
        Read info from the doc file and convert it, after it call save.
        :param previous:
        :param file: path to file
        """
        root_files_binary = []
        root_files = []
        File = namedtuple('File', ['name', 'first_block', 'attr'])
        with open(file, 'rb') as f:
            f.read(previous)
            for _ in range(self.num_of_files):
                root_files_binary.append(f.read(self.name_size + self.first_block_num + self.atr_size))
        for file in root_files_binary:
            file = File(codecs.decode(struct.unpack('12sll', file)[0], 'UTF-8').strip('\x00'),
                        struct.unpack('12sll', file)[1],
                        struct.unpack('12sll', file)[2])
            if file.name:
                root_files.append(file)
            else:
                break
        self.save_inf(root_files)
        return root_files

    def save_inf(self, files: list):
        """ Save info from root in Root.txt"""
        with open('Root.txt', 'w') as f:
            f.write(f"Root(name size: {self.name_size} bytes, "
                    f"first_block: {self.first_block_num}bytes, "
                    f"attributes: {self.atr_size} bytes)"
                    f"\n There ara {self.num_of_files} files:")
            for file in files:
                f.write(f"\n\t >{file.name} (first block: {file.first_block}): type - {file.attr}")
        print('Root information saved in Root.txt')


def read_file(place, data, system_size, block_size, fat_table):
    """
    Read file content
    :param place: number of block
    :param data: where we read
    :param system_size: size of superblock, fat and root
    :param block_size: size of block
    :param fat_table:
    :return: content - b-string with file content
    """
    content = b''
    with open(data, 'rb') as f:
        f.read(system_size)
        f.read(block_size * place)
        content += f.read(block_size)
    if fat_table[place][1] not in (-1, 0, 254, 255):
        content += read_file(fat_table[place][1], data, system_size, block_size, fat_table)
    return content


def show_text_files(files_path: list, files_blocks: list, data: str, system_size: int, block_size: int,
                    fat_table: list):
    for path, first_block in zip(files_path, files_blocks):
        if '.txt' in path:
            print(path)
            content = read_file(first_block, data, system_size, block_size, fat_table)
            print('Content in binary:\n')
            print(content)


def save_file_content(files_attr: list, files_blocks: list, data: str,
                      system_size: int, block_size: int, fat_table: list, files_names: list, user_input=False):
    """
    Save the file content in binary to file with same name
    :param user_input: for test with determine input
    :param files_names: names of files
    :param files_path: paths to file
    :param files_attr:
    :param files_blocks: files first blocks
    :param data: where we read inf
    :param system_size: size of superblock, fat and root
    :param block_size: size of block
    :param fat_table:
    :return: massage about results of work
    """
    if not user_input:
        user_input = input('Enter full file path in format /..../... : ')
    if user_input in files_names:
        position = files_names.index(user_input)
        if files_attr[position] == 1:
            return "It's a folder"
        result = read_file(files_blocks[position], data, system_size, block_size, fat_table)
        with open(files_names[position], 'w') as f:
            print(result, file=f)
        return f'File saved in {files_names[position]}'
    return 'Wrong path'


def search(file_list: list, files_path: list, print_info=True, user_input=False):
    """
    Search files for user
    :param user_input: user input for test
    :param print_info: print information or just return
    :param file_list: list of files' names
    :param files_path: list of files' paths
    :return:
    """
    if not user_input:
        user_input = input('Enter what are you looking for: ')
    search_result = []
    for file, path in zip(file_list, files_path):
        if user_input in file:
            search_result.append(path)
    if print_info:
        print(search_result)
        with open('Search_results.txt', 'w') as f:
            print(search_result, file=f)
        print("Search results saved in Search_results.txt")
    else:
        return search_result


def built_tree(files_paths: list, files_attr: list, files_first_blocks: list):
    """
    Show all file with their info and saves results
    :param files_paths:
    :param files_attr:
    :param files_first_blocks:
    :return:
    """
    with open('File_map.txt', 'w') as f:
        for path, block, attr in zip(files_paths, files_first_blocks, files_attr):
            tab = path.count('/') - 1
            print('\t' * tab + path + f": first block: {block}, type: {attr}")
            f.write('\t' * tab + path + f": first block: {block}, type: {attr}\n")
    print('File tree saved in File_map.txt')


def make_paths(file_map: dict, prefix='/'):
    """
    Make list of files path and files info from dict
    :param file_map: dict of files
    :param prefix: previous path
    :return: storage - namedtuple with filenames, paths, their fist blocks and attr
    """
    Storage = namedtuple('Storage', ['names', 'paths', 'first_blocks', 'attr'])
    storage = Storage([], [], [], [])
    for file in file_map:
        storage.paths.append(prefix + file.name)
        storage.names.append(file.name)
        storage.first_blocks.append(file.first_block)
        storage.attr.append(file.attr)
        if file.attr == 1:
            inner_part = make_paths(file_map[file], prefix + file.name + '/')
            storage.names.extend(inner_part.names)
            storage.paths.extend(inner_part.paths)
            storage.first_blocks.extend(inner_part.first_blocks)
            storage.attr.extend(inner_part.attr)
    return storage


def find_inner_file(file_list: list, system_size: int, block_size: int, file_path: str,
                    file_length: int, fat_table: list):
    """
    Find files in folders
    :param file_list: where should we check folders
    :param system_size: size of root, FAT and superblock
    :param block_size: size of block
    :param file_path: path to data file
    :param file_length: length of file info
    :param fat_table:
    :return: file map -- all file
    """
    file_map = {}
    File = namedtuple('File', ['name', 'first_block', 'attr'])
    inner_content_binary = []
    inner_content = []
    for file in file_list:
        if file.attr == 1:
            while True:
                with open(file_path, 'rb') as f:
                    f.read(system_size)
                    f.read(block_size * file.first_block)
                    inner_content_binary.append(f.read(file_length))
                    if fat_table[file.first_block][1] in (-1, 0, 254, 255):
                        break
            for fb in inner_content_binary:
                fb = File(codecs.decode(struct.unpack('12sll', fb)[0], 'UTF-8').strip('\x00'),
                          struct.unpack('12sll', fb)[1],
                          struct.unpack('12sll', fb)[2])
                inner_content.append(fb)
            inner_content = find_inner_file(inner_content, system_size, block_size, file_path, file_length,
                                            fat_table)
            file_map[file] = inner_content
        else:
            file_map[file] = 'Not Folder'
    return file_map


def main():
    superblock = Superblock('v12.dat', 12)
    fat = FatBlock(superblock.size_of_fat, 4, superblock.size, 'v12.dat')
    root = RootBlock(superblock.size_of_root, 12, 4, 4, superblock.size + fat.size, 'v12.dat')
    file_map = find_inner_file(root.root_files, superblock.size + fat.size + superblock.size_of_root * 20,
                               superblock.size_of_block, 'v12.dat', 20, fat.fat_table)
    files_storage = make_paths(file_map)
    while True:
        print('Choose option:'
              '\n 1 - Show Superblock info'
              '\n 2 - Show FAT info'
              '\n 3 - Show Root info'
              '\n 4 - Show detail Superblock info'
              '\n 5 - Show detail FAT info'
              '\n 6 - Show detail Root info'
              '\n 7 - Search'
              '\n 8 - Show file map'
              '\n 9 - Save file'
              '\n 10 - Show content of .txt files'
              '\n Press anything else to exit')
        option = input()
        if option == '1':
            print("\n**************************************")
            print(superblock)
            print("**************************************\n")
        elif option == '2':
            print("\n**************************************")
            print(fat)
            print("**************************************\n")
        elif option == '3':
            print("\n**************************************")
            print(root)
            print("**************************************\n")
        elif option == '4':
            print("\n**************************************")
            print(repr(superblock))
            print("**************************************\n")
        elif option == '5':
            print("\n**************************************")
            print(repr(fat))
            print("**************************************\n")
        elif option == '6':
            print("\n**************************************")
            print(repr(root))
            print("**************************************\n")
        elif option == '7':
            print("\n**************************************")
            search(files_storage.names, files_storage.paths)
            print("**************************************\n")
        elif option == '8':
            print("\n**************************************")
            built_tree(files_storage.paths, files_storage.attr, files_storage.first_blocks)
            print("**************************************\n")
        elif option == '9':
            print("\n**************************************")
            print(save_file_content(files_storage.paths, files_storage.attr, files_storage.first_blocks, 'v12.dat',
                                    superblock.size + fat.size + superblock.size_of_root * 20, superblock.size_of_block,
                                    fat.fat_table, files_storage.names))
            print("**************************************\n")
        elif option == '10':
            print("\n**************************************")
            show_text_files(files_storage.paths, files_storage.first_blocks, 'v12.dat',
                            superblock.size + fat.size + superblock.size_of_root * 20, superblock.size_of_block,
                            fat.fat_table)
            print("**************************************\n")
        else:
            print('Good bye')
            break


if __name__ == '__main__':
    main()
