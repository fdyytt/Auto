def load_config(filename):
    config = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                config[key] = value
        return config
    except FileNotFoundError:
        print("File tidak ditemukan")
        return None

filename = '/storage/emulated/0/bot/config.txt'
config = load_config(filename)

if config:
    print("Konfigurasi:")
    for key, value in config.items():
        print(f"{key} = {value}")