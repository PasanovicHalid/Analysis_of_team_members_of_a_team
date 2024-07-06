
def save_headers_to_file(df, filename):
    with open(filename, 'w') as f:
        for header in df.columns:
            f.write(header + '\n')