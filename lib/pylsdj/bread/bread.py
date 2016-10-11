import types
import collections
import functools
import json
import math

from bitstring import BitArray, pack, CreationError

from .vendor import six
from .vendor.six.moves import range

LITTLE_ENDIAN = 0
BIG_ENDIAN = 1
CONDITIONAL = 2

# Enumeration of different operations that field descriptors can perform
READ = 0
WRITE = 1

class BadConditionalCaseError(Exception):
    def __init__(self, case):
        super(BadConditionalCaseError, self).__init__(
            "No known conditional case '%s'" % (case))

def indent_text(string, indent_level=2):
    """Indent every line of text in a newline-delimited string"""
    indented_lines = []

    indent_spaces = ' ' * indent_level

    for line in string.split('\n'):
        indented_lines.append(indent_spaces + line)

    return '\n'.join(indented_lines)

class BreadField(object):
    def __init__(self, length, encode_fn, decode_fn, str_format):
        self._data_bits = None
        self.__offset = None
        self._length = length
        self._cached_value = None

        self._encode_fn = encode_fn
        self._decode_fn = decode_fn

        self._str_format = str_format

        self._name = None

    @property
    def _offset(self):
        return self.__offset

    @_offset.setter
    def _offset(self, value):
        self.__offset = value
        self._cached_value = None

    def _set_data(self, data_bits):
        self._data_bits = data_bits

    def __eq__(self, other):
        if not isinstance(other, BreadField):
            return False

        return self.get() == other.get()

    def __ne__(self, other):
        return not self.__eq__(other)

    def get(self):
        if self._cached_value is None:
            if self._offset is None:
                raise AttributeError(
                    "Haven't initialized the field '%s' with offsets yet" %
                    (self._name))

            start_bit = self._offset
            end_bit = self._offset + self._length

            value_bits = self._data_bits[start_bit:end_bit]
            self._cached_value = self._decode_fn(value_bits)

        return self._cached_value

    def as_native(self):
        return self.get()

    def __str__(self):
        return str(self.get())

    def set(self, value):
        value_bits = self._encode_fn(value)

        self._data_bits.overwrite(value_bits, self._offset)

        self._cached_value = value

class BreadConditional(object):
    @staticmethod
    def from_spec(spec, parent):
        predicate_field_name, conditions = spec[1:]

        field = BreadConditional(predicate_field_name, parent)

        for predicate_value, condition in list(conditions.items()):
            condition_struct = build_struct(condition)
            field._add_condition(predicate_value, condition_struct)

        return field

    def __init__(self, conditional_field_name, parent_struct):
        self._parent_struct = parent_struct
        self._conditional_field_name = conditional_field_name
        self._conditions = {}
        self._name = None


    def _set_data(self, data_bits):
        for struct in list(self._conditions.values()):
            struct._set_data(data_bits)

    def _add_condition(self, predicate_value, struct):
        self._conditions[predicate_value] = struct

    def _get_condition(self):
        switch_value = getattr(
            self._parent_struct, self._conditional_field_name)

        if switch_value not in self._conditions:
            raise BadConditionalCaseError(str(switch_value))

        return switch_value

    def __getattr__(self, attr):
        return getattr(self._conditions[self._get_condition()], attr)

    def __setattr__(self, attr, value):
        if attr[0] == '_':
            super(BreadConditional, self).__setattr__(attr, value)
        else:
            self._conditions[self._get_condition()].__setattr__(attr, value)

    @property
    def _length(self):
        return list(self._conditions.values())[0]._length

    def as_native(self):
        return self._conditions[self._get_condition()].as_native()

    def __str__(self):
        return '\n'.join(
            self._conditions[self._get_condition()]._field_strings())

    @property
    def _offset(self):
        return self._conditions[list(self._conditions.keys())[0]]._offset

    @_offset.setter
    def _offset(self, off):
        for condition_struct in list(self._conditions.values()):
            condition_struct._offset = off

class BreadArray(object):
    def __init__(self, num_items, parent, item_spec, field_options):
        self._num_items = num_items
        self.__offset = None
        self._name = None
        self._item_length = None
        self._accessor_items = [None] * self._num_items
        self._item_spec = item_spec
        self._parent = parent
        self._data_bits = None
        self._field_options = field_options

        self._item_length = self._get_accessor_item(0)._length

    @property
    def _offset(self):
        return self.__offset

    @_offset.setter
    def _offset(self, offset):
        self.__offset = offset

        cached_accessors = (i for i in self._accessor_items if i is not None)

        for item in cached_accessors:
            item._offset = offset


    def _create_accessor_item(self, index):
        if type(self._item_spec) == list:
            item = build_struct(self._item_spec)
        elif (type(self._item_spec) == tuple and
              self._item_spec[0] == CONDITIONAL):
            item = BreadConditional.from_spec(self._item_spec, self._parent)
        else:
            item = self._item_spec(self._parent, **(self._field_options))

        if self._offset is not None:
            item._offset = index * self._item_length + self._offset

        if self._data_bits is not None:
            item._set_data(self._data_bits)

        return item

    def _get_accessor_item(self, index):
        if self._accessor_items[index] is None:
            self._accessor_items[index] = self._create_accessor_item(index)

        return self._accessor_items[index]

    def __str__(self):
        string_repr = '['

        if self._num_items > 0:
            if type(self._item_spec) == list:
                str_function =  lambda x: '\n' + indent_text(str(x))
            else:
                str_function = str

            item_strings = []

            for i in range(self._num_items):
                item_strings.append(str_function(self[i]))

            string_repr += ', '.join(item_strings)

        string_repr += ']'

        return string_repr

    @property
    def _length(self):
        return self._item_length * self._num_items

    def __getitem__(self, index):
        if type(index) is slice:
            start, stop, step = index.indices(self._num_items)

            return [self._get_accessor_item(i).get()
                    for i in range(start, stop, step)]
        else:
            if index < 0 or index >= self._num_items:
                raise IndexError('list index out of range')

            return self._get_accessor_item(index).get()

    def __setitem__(self, index, value):
        if index < 0 or index >= self._num_items:
            raise IndexError('list index out of range')

        self._get_accessor_item(index).set(value)

    def __len__(self):
        return self._num_items

    def __eq__(self, other):
        if isinstance(other, list):
            return [self[i] for i in range(self._num_items)] == other

        if not isinstance(other, BreadArray):
            return False

        if self._num_items != other._num_items:
            return False

        for i in range(self._num_items):
            if self[i] != other[i]:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def get(self):
        return self

    def set(self, value):
        if type(value) != list:
            raise ValueError('Cannot set an array using a %s value' %
                             (str(type(value))))
        if len(value) != self._num_items:
            raise ValueError(
                'Cannot change the length of an array '
                '(would have changed from %d to %d)'
                % (self._num_items, len(value)))

        for i, item in enumerate(value):
            self._get_accessor_item(i).set(item)

    def as_native(self):
        native_items = []

        for i in range(self._num_items):
            native_items.append(self._get_accessor_item(i).as_native())

        return native_items

    def _set_data(self, data_bits):
        self._data_bits = data_bits

        cached_accessors = (i for i in self._accessor_items if i is not None)

        for item in cached_accessors:
            item._set_data(data_bits)

class BreadStruct(object):
    def __init__(self):
        self._data_bits = None
        self._fields = {}
        self._conditional_fields = []
        self._field_list = []
        self._name = None

        # __offsets__ retained for backwards compatibility
        class Offsets(object):
            pass
        self.__offsets__ = Offsets()

    def __eq__(self, other):
        if not hasattr(other, '_data_bits'):
            return False

        return self._data_bits == other._data_bits

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return self._LENGTH

    @property
    def _length(self):
        return self._LENGTH

    def _field_strings(self):
        field_strings = []

        for field in self._field_list:
            if isinstance(field, BreadStruct):
                field_strings.append(
                    field._name + ': ' + indent_text(str(field)).lstrip())
            elif isinstance(field, BreadConditional):
                field_strings.append(str(field))
            else:
                if field._name[0] != '_':
                    field_strings.append(field._name + ': ' + str(field))

        return field_strings

    def __str__(self):
        field_strings = self._field_strings()
        return '{\n' + '\n'.join(map(indent_text, field_strings)) + '\n}'

    def _set_data(self, data_bits):
        self._data_bits = data_bits

        for field in self._field_list:
            field._set_data(data_bits)

    @property
    def _offset(self):
        # A struct's offset is the offset where its first field starts
        return self._field_list[0]._offset

    @_offset.setter
    def _offset(self, value):
        offset = value

        # All fields offsets are relative to the starting offset for the struct
        for field in self._field_list:
            field._offset = offset
            offset += field._length

        for name, field in list(self._fields.items()):
            setattr(self.__offsets__, name, field._offset)

    # _LENGTH retained for backwards compatibility
    @property
    def _LENGTH(self):
        return sum([x._length for x in self._field_list])

    def get(self):
        return self

    def set(self, value):
        raise ValueError("Can't set a non-leaf struct to a value")

    def __getattr__(self, attr):
        if attr in self._fields:
            return self._fields[attr].get()

        for conditional_field in self._conditional_fields:
            try:
                return getattr(conditional_field, attr)
            except AttributeError:
                pass #pragma: no cover

        raise AttributeError("No known field '%s'" % (attr))

    def __setattr__(self, attr, value):
        try:
            if attr[0] == '_':
                super(BreadStruct, self).__setattr__(attr, value)
            elif attr in self._fields:
                field = self._fields[attr]
                field.set(value)
            else:
                for conditional_field in self._conditional_fields:
                    try:
                        return setattr(conditional_field, attr, value)
                    except AttributeError:
                        pass

                raise AttributeError("No known field '%s'" % (attr))
        except CreationError as e:
            raise ValueError('Error while setting %s: %s' % (field._name, e))

    def _add_field(self, field, name):
        if name is not None:
            self._fields[name] = field
            field._name = name

        self._field_list.append(field)

        if isinstance(field, BreadConditional):
            self._conditional_fields.append(field)

    def as_native(self):
        native_struct = {}

        for field in self._field_list:
            if isinstance(field, BreadConditional):
                native_struct.update(field.as_native())
            elif field._name[0] != '_':
                native_struct[field._name] = field.as_native()
            elif isinstance(field, BreadConditional):
                native_struct.update(field.as_native())

        return native_struct

    def as_json(self):
        return json.dumps(self.as_native())


# BEGIN TYPE INFORMATION

def intX(length, signed=False):
    def make_intX_field(parent, **field_options):
        if length % 8 == 0 and length >= 8:
            int_type_key = None

            if signed:
                int_type_key = 'int'
            else:
                int_type_key = 'uint'

            if field_options.get('endianness', None) == BIG_ENDIAN:
                int_type_key += 'be'
            else:
                int_type_key += 'le'

            offset = field_options.get('offset', 0)

            def encode_intX(value):
                options = {}
                options[int_type_key] = value - offset
                options['length'] = length

                return BitArray(**options)

            def decode_intX(encoded):
                return getattr(encoded, int_type_key) + offset
        else:
            offset = field_options.get('offset', 0)

            def encode_intX(value):
                value -= offset

                if signed:
                    return BitArray(int=value, length=length)
                else:
                    return BitArray(uint=value, length=length)

            def decode_intX(encoded):
                if signed:
                    decoded = encoded.int
                else:
                    decoded = encoded.uint

                return decoded + offset


        return BreadField(
            length, encode_intX, decode_intX,
            str_format=field_options.get('str_format', None))

    return make_intX_field

uint8  = intX(length=8,  signed=False)
byte = uint8
uint16 = intX(length=16, signed=False)
uint32 = intX(length=32, signed=False)
uint64 = intX(length=64, signed=False)
int8   = intX(length=8,  signed=True)
int16  = intX(length=16, signed=True)
int32  = intX(length=32, signed=True)
int64  = intX(length=64, signed=True)
bit = intX(1, signed=False)
semi_nibble = intX(2, signed=False)
nibble = intX(4, signed=False)

def string(length):
    def make_string_field(parent, **field_options):
        length_in_bits = length * 8

        def encode_string(value):
            if type(value) != bytes:
                value = value.encode('utf-8')

            return BitArray(bytes=value)

        def decode_string(encoded):
            return encoded.bytes

        return BreadField(length_in_bits, encode_string, decode_string,
                          str_format=field_options.get('str_format', None))

    return make_string_field

def encode_bool(value):
    return BitArray(bool=value)

def decode_bool(encoded):
    return encoded.bool

def boolean(parent, **field_options):
    return BreadField(
        1, encode_bool, decode_bool,
        str_format=field_options.get('str_format', None))

def padding(length): # pragma: no cover
    def make_padding_field(parent, **field_options):
        def encode_pad(value):
            return pack('pad:n', n=value)

        def decode_pad(encoded):
            return None

        return BreadField(
            length, encode_pad, decode_pad,
            str_format=field_options.get('str_format', None))

    return make_padding_field

def enum(length, values, default=None):
    def make_enum_field(parent, **field_options):
        enum_field = intX(length, signed=False)(parent, **field_options)

        old_encode_fn = enum_field._encode_fn
        old_decode_fn = enum_field._decode_fn

        keys = {v: k for k, v in list(values.items())}

        def encode_enum(key):
            if key not in keys:
                raise ValueError('%s is not a valid enum value' % (key))

            return old_encode_fn(keys[key])

        def decode_enum(encoded):
            decoded_value = old_decode_fn(encoded)

            if decoded_value not in values:
                if default is not None:
                    return default
                else:
                    raise ValueError(
                        '%d is not a valid enum value' % (decoded_value))

            return values[decoded_value]

        enum_field._encode_fn = encode_enum
        enum_field._decode_fn = decode_enum

        return enum_field

    return make_enum_field

def array(length, substruct):
    def make_array_field(parent, **field_options):
        return BreadArray(length, parent, substruct, field_options)

    return make_array_field

# END TYPE INFORMATION

def build_struct(spec, type_name=None):
    # Give different structs the appearance of having different type names
    class NewBreadStruct(BreadStruct):
        pass

    if type_name is not None:
        NewBreadStruct.__name__ = type_name

    struct = NewBreadStruct()

    global_options = {}

    unnamed_fields = 0

    for spec_line in spec:
        if type(spec_line) == dict:
            # A dictionary in the spec indicates global options for parsing
            global_options = spec_line
        elif isinstance(spec_line, types.FunctionType) or len(spec_line) == 1:
            # This part of the spec doesn't have a name; evaluate the function
            # to get the field object and then give that object a fake name.
            # Spec lines of length 1 are assumed to be functions.

            if isinstance(spec_line, types.FunctionType):
                field = spec_line
            else:
                field = spec_line[0]

            # Don't give the field a name
            struct._add_field(
                field(struct, **global_options), '_unnamed_%d' %
                (unnamed_fields))
            unnamed_fields += 1

        elif spec_line[0] == CONDITIONAL:
            predicate_field_name, conditions = spec_line[1:]

            field = BreadConditional.from_spec(spec_line, struct)

            struct._add_field(
                field, '_conditional_on_%s_%d' %
                (predicate_field_name, unnamed_fields))
            unnamed_fields += 1
        else:
            field_name = spec_line[0]
            field = spec_line[1]
            options = global_options

            # Options for this field, if any, override the global options
            if len(spec_line) == 3:
                options = global_options.copy()
                options.update(spec_line[2])

            if type(field) == list:
                struct._add_field(build_struct(field), field_name)
            else:
                struct._add_field(field(struct, **options), field_name)

    return struct


def new(spec, type_name='bread_struct', data=None):
    struct = build_struct(spec, type_name)

    if data is None:
        data = BitArray(bytearray(int(math.ceil(len(struct) / 8.0))))

    if len(struct) > len(data):
        raise ValueError(
            ("Data being parsed isn't long enough; expected at least %d "
             "bits, but data is only %d bits long") %
            (len(struct), len(data)))

    struct._set_data(data[:len(struct)])
    struct._offset = 0

    return struct

def parse(data_source, spec, type_name='bread_struct'):
    if type(data_source) == str:
        data_bits = BitArray(bytes=six.b(data_source))
    elif type(data_source) == list:
        data_bits = BitArray(bytes=data_source)
    else:
        data_bits = BitArray(data_source)

    return new(spec, type_name=type_name, data=data_bits)

def write(parsed_obj, spec=None, filename=None):
    """Writes an object created by `parse` to either a file or a bytearray.

    If the object doesn't end on a byte boundary, zeroes are appended to it
    until it does.
    """
    if not isinstance(parsed_obj, BreadStruct):
        raise ValueError(
            'Object to write must be a structure created '
            'by bread.parse')

    if filename is not None:
        with open(filename, 'wb') as fp:
            parsed_obj._data_bits.tofile(fp)
    else:
        return bytearray(parsed_obj._data_bits.tobytes())
