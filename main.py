import re
import requests
import config
from collections import OrderedDict

def parse_template(template_file):
    """
    Parse the template file to extract channel names.
    """
    template_channels = OrderedDict()
    current_category = None

    with open(template_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "#genre#" in line:
                    current_category = line.split(",")[0].strip()
                    template_channels[current_category] = []
                elif current_category:
                    channel_name = line.split(",")[0].strip()
                    template_channels[current_category].append(channel_name)

    return template_channels

def getChannelItems(template_channels, source_urls):
    """
    Get the channel items from the source URLs
    """
    channels = OrderedDict()

    for category in template_channels:
        channels[category] = OrderedDict()

    for url in source_urls:
        if url.endswith(".m3u"):
            converted_url = f"https://fanmingming.com/txt?url={url}"
            response = requests.get(converted_url)
        else:
            response = requests.get(url)

        if response.status_code == 200:
            response.encoding = 'utf-8'
            lines = response.text.split("\n")

            current_category = None

            for line in lines:
                line = line.strip()
                if "#genre#" in line:
                    current_category = line.split(",")[0].strip()
                else:
                    match = re.match(r"^(.*?),(?!#genre#)(.*?)$", line)
                    if match and current_category in channels:
                        channel_name = match.group(1).strip()
                        if channel_name in template_channels[current_category]:
                            channels[current_category].setdefault(channel_name, []).append(match.group(2).strip())
        else:
            print(f"Failed to fetch channel items from the source URL: {url}")

    return channels

def filter_source_urls(template_file):
    """
    Filter source URL.
    """
    template_channels = parse_template(template_file)
    source_urls = config.source_urls
    return getChannelItems(template_channels, source_urls), template_channels

def updateChannelUrlsM3U(channels, template_channels):
    """
    Update the category and channel URLs to the final file in M3U format
    """
    written_urls = set()  # Set to store written URLs

    with open("live.m3u", "w", encoding="utf-8") as f_m3u:
        f_m3u.write("#EXTM3U\n")
        f_m3u.write("""#EXTINF:-1 tvg-id="1" tvg-name="请阅读" tvg-logo="https://gitee.com/yuanzl77/TVBox-logo/raw/main/mmexport1713580051470.png" group-title="公告",请阅读\n""")
        f_m3u.write("https://liuliuliu.tv/api/channels/1997/stream\n")
        f_m3u.write("""#EXTINF:-1 tvg-id="1" tvg-name="yuanzl77.github.io" tvg-logo="https://gitee.com/yuanzl77/TVBox-logo/raw/main/mmexport1713580051470.png" group-title="公告",yuanzl77.github.io\n""")
        f_m3u.write("https://liuliuliu.tv/api/channels/233/stream\n")

        with open("live.txt", "w", encoding="utf-8") as f_txt:
            for category, channel_list in template_channels.items():
                f_txt.write(f"{category},#genre#\n")
                if category in channels:
                    for channel_name in channel_list:
                        if channel_name in channels[category]:
                            for url in channels[category][channel_name]:
                                if url and url not in written_urls:  # Check if URL is not already written
                                    f_m3u.write(f"#EXTINF:-1 tvg-id=\"\" tvg-name=\"{channel_name}\" tvg-logo=\"https://gitee.com/yuanzl77/TVBox-logo/raw/main/png/{channel_name}.png\" group-title=\"{category}\",{channel_name}\n")
                                    f_m3u.write(url + "\n")
                                    f_txt.write(f"{channel_name},{url}\n")
                                    written_urls.add(url)  # Add URL to written URLs set

            f_txt.write("\n")

if __name__ == "__main__":
    template_file = "demo.txt"
    channels, template_channels = filter_source_urls(template_file)
    updateChannelUrlsM3U(channels, template_channels)
