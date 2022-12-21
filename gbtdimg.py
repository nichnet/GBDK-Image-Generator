import constants
import sys
import example_data
import decoder
import encoder


if __name__ == "__main__":
    args = sys.argv
    mode = args[1]
    path = args[2]

    name = ''
    if mode == '-d':
        data = None
        if path in ['t88', 't816', 't1616', 't3232']: 
            if path == 't88':
                data = example_data.t8_8["data"]
                name = example_data.t8_8["name"]
            elif path == 't816':
                data = example_data.t8_16["data"]
                name = example_data.t8_16["name"]
            elif path == 't1616':
                data = example_data.t16_16["data"]
                name = example_data.t16_16["name"]
            elif path == 't3232':
                data = example_data.t32_32["data"]
                name = example_data.t32_32["name"]
        else:
            name = args[2]
            if len(args) >= 4:
                #this allows us to enter data such as (eg)
                #0x6c,0x6c,0xfe,0x92,0xd6,0xaa,0xc6,0xba OR 
                #0x6c, 0x6c, 0xfe, 0x92, 0xd6, 0xaa, 0xc6, 0xba, OR 
                #0x6c 0x6c 0xfe 0x92 0xd6 0xaa 0xc6 0xba
                raw = args[3:len(args)]
                data = []
                for o in raw:
                    for h in o.split(','):
                        try:
                            data.append(int(h.strip(), 16))
                        except:
                            #invalid hex, eg a ''
                            #ignore
                            pass

        if data == None:
            print('No data to decode.') 
        else:
            pass
            print(f'Decoding data ({name}) and exporting as file: {constants.EXPORT_FOLDER}/{name}.png') 
            quads = encoder.generateQuadrants(data)
            ordered = encoder.sortQuadrants(quads)
            encoder.exportImage(name, ordered)


    elif mode == '-e':
        name = args[3]
        print(f'Decoding example image ({name})')

        if path and name:
            arr = decoder.decompileImageFile(path)

            out = []

            for i in range(0, len(arr), 16):
                out.append(arr[i:i+16])

            unsorted = decoder.sortQuadrantsForDecompile(out)

            decoder.exportCOutFIle(name, unsorted)
            print(f'Exporting out files: {constants.EXPORT_FOLDER}/{name}.c & {constants.EXPORT_FOLDER}/{name}.h')


            


