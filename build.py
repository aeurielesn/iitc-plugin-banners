import os
import json
import hashlib
import shutil

build_directory = "build"
providers_url = "b/%banner%.json"


def path(provider, directory=""):
    filename = providers_url.replace("%banner%", provider)
    filename = os.path.dirname(os.path.realpath(__file__)) + directory + filename
    return filename


def dpath(provider):
    filename = path(provider, "/" + build_directory)
    dirname = os.path.dirname(os.path.realpath(filename))
    print dirname
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return filename


def hash(banner):
    with open(path(banner)) as data:
        contents = data.read()
        include = json.loads(contents)
        sha256 = hashlib.sha256(contents).hexdigest()
        print "%s: %s" % (banner, sha256,)
        shutil.copy(path(banner), dpath("%s$%s" % (banner, sha256)))

    return include, sha256


def generate(provider):
    provider_length = 0

    with open(path(provider)) as data:
        include = json.load(data)

        for subprovider in include.get("providers", []):
            print "building: %s" % (subprovider,)
            metadata, sha256, subprovider_length = generate(subprovider)
            include["providers"][subprovider]["name"] = metadata["name"]
            include["providers"][subprovider]["sha256"] = sha256
            include["providers"][subprovider]["length"] = subprovider_length
            provider_length += subprovider_length

        for banner in include.get("banners", []):
            print "hashing: %s" % (banner,)
            metadata, sha256 = hash(banner)
            include["banners"][banner]["name"] = metadata["name"]
            include["banners"][banner]["authors"] = metadata["authors"]
            include["banners"][banner]["sha256"] = sha256
            include["banners"][banner]["length"] = len(metadata.get("missions", []))

        provider_length += len(include.get("banners", []))

    return include, dump(provider, include), provider_length


def dump(provider, include):
    contents = json.dumps(include, indent=2)
    sha256 = hashlib.sha256(contents).hexdigest()
    # print "%s: %s" % (provider, sha256,)
    output_file = dpath("%s$%s" % (provider, sha256))
    with open(output_file, "wb") as f:
        f.write(contents)
    return sha256

if not os.path.exists(build_directory):
    os.makedirs(build_directory)

if not os.path.exists(os.path.join(build_directory, "b")):
    os.makedirs(os.path.join(build_directory, "b"))

with open("banners.json") as data:
    root = json.load(data)

    if "providers-url" in root:
        providers_url = root["providers-url"].replace("%hash%", "").replace("$", "")

    if "providers" in root:
        for provider in root["providers"]:
            print "building: %s" % (provider,)
            metadata, sha256, provider_length = generate(provider)
            root["providers"][provider]["name"] = metadata["name"]
            root["providers"][provider]["sha256"] = sha256
            root["providers"][provider]["length"] = provider_length

    output_file = os.path.join(build_directory, "banners.json")
    with open(output_file, "wb") as f:
        json.dump(root, f, indent=2)
