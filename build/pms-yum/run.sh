_SERVER="192.168.92.100"

mount |grep "^$_SERVER:/export/migasfree" >/dev/null
if [ $? -ne 0 ]
then
    mount -t nfs $_SERVER:/export/migasfree /var/lib/migasfree
fi

docker run --rm -ti \
  -v "/var/lib/migasfree/$_SERVER/public:/var/migasfree/repo" \
  -v "/var/lib/migasfree/$_SERVER/keys:/usr/share/migasfree-server" \
  migasfree/apt:latest \
  su -c "/app/repository-create 1" - www-data

mkdir /var/migasfree
chown 890:890 /var/migasfree
su -c "/app/repository-create 1" www-data
