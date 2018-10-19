#
# -------------------------------------------------------------------------
#   Copyright (c) 2018 AT&T Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#

#!/bin/bash
#
#	This script sets up the AAF internal certificate authority as a
#	recognized certificate authority.
#
#	This script must be run as root.
#	Works on both CentOS and Ubuntu.
#
set -x
cat >/tmp/aafcacert.crt <<'!EOF'
-----BEGIN CERTIFICATE-----
MIIFPjCCAyagAwIBAgIJAJ6u7cCnzrWdMA0GCSqGSIb3DQEBCwUAMCwxDjAMBgNV
BAsMBU9TQUFGMQ0wCwYDVQQKDARPTkFQMQswCQYDVQQGEwJVUzAeFw0xODA0MDUx
NDE1MjhaFw0zODAzMzExNDE1MjhaMCwxDjAMBgNVBAsMBU9TQUFGMQ0wCwYDVQQK
DARPTkFQMQswCQYDVQQGEwJVUzCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoC
ggIBAMA5pkgRs7NhGG4ew5JouhyYakgYUyFaG121+/h8qbSdt0hVQv56+EA41Yq7
XGie7RYDQK9NmAFF3gruE+6X7wvJiChp+Cyd7sFMnb65uWhxEdxWTM2BJFrgfzUn
H8ZCxgaCo3XH4PzlKRy2LQQJEJECwl/RZmRCXijMt5e9h8XoZY/fKkKcZZUsWNCM
pTo266wjvA9MXLmdgReRj0+vrCjrNqy+htwJDztoiHWiYPqT6o8EvGcgjNqjlZx7
NUNf8MfLDByqKF6+wRbHv1GKjn3/Vijd45Fv8riyRYROiFanvbV6jIfBkv8PZbXg
2VDWsYsgp8NAvMxK+iV8cO+Ck3lBI2GOPZbCEqpPVTYbLUz6sczAlCXwQoPzDIZY
wYa3eR/gYLY1gP2iEVHORag3bLPap9ZX5E8DZkzTNTjovvLk8KaCmfcaUMJsBtDd
ApcUitz10cnRyZc1sX3gE1f3DpzQM6t9C5sOVyRhDcSrKqqwb9m0Ss04XAS9FsqM
P3UWYQyqDXSxlUAYaX892u8mV1hxnt2gjb22RloXMM6TovM3sSrJS0wH+l1nznd6
aFXftS/G4ZVIVZ/LfT1is4StoyPWZCwwwly1z8qJQ/zhip5NgZTxQw4mi7ww35DY
PdAQOCoajfSvFjqslQ/cPRi/MRCu079heVb5fQnnzVtnpFQRAgMBAAGjYzBhMB0G
A1UdDgQWBBRTVTPyS+vQUbHBeJrBKDF77+rtSTAfBgNVHSMEGDAWgBRTVTPyS+vQ
UbHBeJrBKDF77+rtSTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBhjAN
BgkqhkiG9w0BAQsFAAOCAgEAPx/IaK94n02wPxpnYTy+LVLIxwdq/kawNd6IbiMz
L87zmNMDmHcGbfoRCj8OkhuggX9Lx1/CkhpXimuYsZOFQi5blr/u+v4mIbsgbmi9
7j+cUHDP0zLycvSvxKHty51LwmaX9a4wkJl5zBU4O1sd/H9tWcEmwJ39ltKoBKBx
c94Zc3iMm5ytRWGj+0rKzLDAXEWpoZ5bE5PLJauA6UDCxDLfs3FwhbS7uDggxYvf
jySF5FCNET94oJ+m8s7VeHvoa8iPGKvXrIqdd7XDHnqJJlVKr7m9S0fMbyEB8ci2
RtOXDt93ifY1uhoEtEykn4dqBSp8ezvNMnwoXdYPDvTd9uCAFeWFLVreBAWxd25h
PsBTkZA5hpa/rA+mKv6Af4VBViYr8cz4dZCsFChuioVebe9ighrfjB//qKepFjPF
CyjzKN1u0JKm/2x/ORqxkTONG8p3uDwoIOyimUcTtTMv42bfYD88RKakqSFXE9G+
Z0LlaKABqfjK49o/tsAp+c5LoNlYllKhnetO3QAdraHwdmC36BhoghzR1jpX751A
cZn2VH3Q4XKyp01cJNCJIrua+A+bx6zh3RyW6zIIkbRCbET+UD+4mr8WIcSE3mtR
ZVlnhUDO4z9//WKMVzwS9Rh8/kuszrGFI1KQozXCHLrce3YP6RYZfOed79LXaRwX
dYY=
-----END CERTIFICATE-----
!EOF
chmod 444 /tmp/aafcacert.crt
if [ -f /etc/redhat-release ]
then
	mv /tmp/aafcacert.crt /etc/pki/ca-trust/source/anchors/aafcacert.pem
	update-ca-trust
else
	mv /tmp/aafcacert.crt /usr/local/share/ca-certificates/aafcacert.crt
	update-ca-certificates
fi
