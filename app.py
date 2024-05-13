from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from Util import count_byte_frequencies, create_huffman_tree, create_encoding_table, encode, decode



app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compress', methods=['GET', 'POST'])
def compress():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join('uploads', filename))

        original_file_path = os.path.join('uploads', filename)
        output_file_path = os.path.join('compressed', filename + '.huff')

        frequency_dict = count_byte_frequencies(original_file_path)
        root = create_huffman_tree(frequency_dict)
        encoding_table = create_encoding_table(root)
        original_size, compressed_size, header_size, compression_rate, header = encode(original_file_path, output_file_path)

        return render_template('compress.html', huffman_table=encoding_table, frequency_dict=frequency_dict, original_size=original_size, header=header, header_size=round(header_size/8), compressed_size=compressed_size, compression_rate=compression_rate*100)
    else:
        return render_template('compress.html', huffman_table={}, frequency_dict={}, original_size=0, compressed_size=0, header_size=0, compression_rate=0)

@app.route('/decompress', methods=['GET', 'POST'])
def decompress():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join('uploads', filename))
            # Remove .huff extension from filename for the decompressed file
            filename_without_extension, _ = os.path.splitext(filename)
            original_size, decompressed_size, header = decode(os.path.join('uploads', filename), os.path.join('decompressed', filename_without_extension))
            return render_template('decompress.html', original_size=original_size, decompressed_size=decompressed_size, header=header)
    else:
        return render_template('decompress.html', original_size=0, decompressed_size=0, header='')

if __name__ == '__main__':
    app.run(debug=True)