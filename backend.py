

def encrypt(frase, key, img_input):
    if img_input[:2] == b'BM':

        st = f'{frase}#'
        bin_code = ''.join(f'{ord(i):012b}' for i in st)
        lt = [bin_code[i:i+key] for i in range(0, len(bin_code), key)]
        img_byte_arr = list(img_input)

        if len(img_byte_arr) - 54 >= len(lt):
            for i in range(len(lt)):
                val = f'{img_byte_arr[i + 54]:08b}'
                img_byte_arr[i + 54] = int(f'{val[:-key]}{lt[i]}', 2)

            return 'The text has been successfully encrypted', bytes(img_byte_arr)
        else:
            return 'The text is too big, choose another image', None
    print(img_input[:10])
    return "This file isn't in BMP24 format", None


def decrypt(key, file_image):
    if file_image[:2] == b'BM':
        img_byte_arr = file_image
        bin_code = ''
        for i in range(54, len(img_byte_arr)):
            val = f'{img_byte_arr[i]:08b}'
            bin_code += val[-key:]
            if len(bin_code) % 12 == 0 and chr(int(bin_code[-12:], 2)) == '#':
                break

        frase = ''.join(chr(int(bin_code[i:i + 12], 2)) for i in range(0, len(bin_code), 12))
        return frase[:-1]
    return "This file isn't in BMP24 format"
