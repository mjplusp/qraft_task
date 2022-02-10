# qraft_task
QRAFT Technologies Sample Task

<!-- # SSL 인증
$ openssl req -x509 -days 365 -newkey rsa:2048 -keyout ./haproxy/certs/key.pem -out ./haproxy/certs/cert.pem -->

각 API 및 사용 쿼리

## GraphQL

## Password 암호화
장고에서는 자동으로 해주지만 회원가입 시 체크해야 할 것은
1. 이메일 중복 체크
2. 패스워드를 암호화해서 저장 (어떻게?)

## JWT 설명, 장단점
1. 사용자가 id와 password를 입력하여 로그인을 시도합니다.
2. 서버는 요청을 확인하고 secret key를 통해 Access token을 발급합니다.
3. JWT 토큰을 클라이언트에 전달 합니다.(토큰이 클라이언트에 저장됨)
4. 클라이언트에서 API 을 요청할때  클라이언트가 Authorization header에 Access token을 담아서 보냅니다.
5. 서버는 JWT Signature를 체크하고 Payload로부터 사용자 정보를 확인해 데이터를 반환합니다.
6. 클라이언트의 로그인 정보를 서버 메모리에 저장하지 않기 때문에 토큰기반 인증 메커니즘을 제공합니다.
인증이 필요한 경로에 접근할 때 서버 측은 Authorization 헤더에 유효한 JWT 또는 존재하는지 확인한다.
JWT에는 필요한 모든 정보를 토큰에 포함하기 때문에 데이터베이스과 같은 서버와의 커뮤니케이션 오버 헤드를 최소화 할 수 있습니다.

회원 인증: JWT 를 사용하는 가장 흔한 시나리오 입니다. 사용자가 로그인을 하면, 서버는 사용자의 정보를 기반으로한 토큰을 발급합니다.
그 후, 사용자가 서버에 요청을 할 때 마다 JWT를 포함하여 전달합니다. 서버는 클라이언트에서 요청을 받을때 마다, 해당 토큰이 유효하고 인증됐는지 검증을 하고, 사용자가 요청한 작업에 권한이 있는지 확인하여 작업을 처리합니다.
서버에서는 사용자에 대한 세션을 유지 할 필요가 없습니다. 즉 사용자가 로그인되어있는지 안되어있는지 신경 쓸 필요가 없고, 사용자가 요청을 했을때 토큰만 확인하면 되므로 세션 관리가 필요 없어서 서버 자원과 비용을 절감할 수 있습니다.

## Simple Backend Auth Server
- REST가 아닌 GraphQL을 사용하여야 함. 
- e-mail과 password를 인자로 회원가입할 수 있음. 
- 회원정보는 DB에 저장되며, password는 암호화 되어 저장 됨. 
- e-mail과 password를 인자로 로그인 할 수 있으며, 이는 json webtoken을 반환 함. 로그인 시, authorization header에 json webtoken이 이미 포함 되어 있는 경우 주어진 json webtoken에 해당하는 email 값을 찾아 "이미 {email}로 로그인 하였습니다."라는 텍스트 를 반환 해야 함. 

## Logging

## Metric Monitoring

Docker 환경 내에서 구동되는 해당 서비스의 특성 상 Container 각각의 Metric 정보와 Host의 Metric 정보를 모두 수집할 필요가 있음.  

이 Task에서는 오픈소스 모니터링 툴인 Prometheus를 이용하였음.  
호스트, 컨테이너의 metric을 수집하는 Exporter 서버가 존재하고, Prometheus 서버는 Exporter Server의 Http EndPoint 주소로 접속해 Metric 데이터를 Scrapping 해옴  
Prometheus는 여러 Exporter로부터 수집한 Metric을 한데 모아 관리.
이후 Grafana와 같은 시각화 툴이 Prometheus 서버에 쿼리를 통해 데이터를 받아와 시각화 하게 되면 호스트와 컨테이너의 CPU 사용량, 메모리, Disk I/O, 네트워크 트래픽 등을 모니터링 할 수 있음

### 구현
본 Task에서는 윈도우 환경에 가상으로 리눅스 환경을 만들어 작업해서 많이 사용되는 컨테이너 및 호스트 Metrics Exporter인 cadvisor, node-exporter가 아닌, container-exporter를 이용했음
container_exporter 컨테이너가 Running 상태에서 http://localhost:9104/metrics 에 접속 후 Export 되고 있는 Container Metric 정보를 확인할 수 있음

## Http TLS

## Load Balancing / Health Check

1. Load Balancing: 클라이언트 수가 많아지며 서버에 부하가 걸리는데, 이를 효율적으로 분산하기 위해 사용
2. Health Check: 로드밸런싱 서비스를 제공하는 서버들의 통신 상태를 점검. 즉 서버가 제대로 서비스를 제공 가능한지 확인
   1. 단순히 서버들의 Network Interface가 up 상태인지만을 확인  
   2. 주기적으로 TCP Connection을 시도  
        - ip에 telnet 접속. 3-way handshake 통해 TCP 채널이 성공적으로 연결되는지 확인  
        - Connection Failed가 일정 횟수 이상 반복될 경우 Load Balancing 시 해당 서버는 제외
   1. 웹 애플리케이션이 잘 구동하고 있는지를 Test할 수도 있음.  
        - 웹 서버는 GET, POST 등 미리 지정된 Http Request를 보내고 서버가 성공 코드를 반환하는지 여부를 이용해 Heal Check할 수도 있음

### 구현
Health Check와 Load Balancing을 지원하는 HAProxy Docker Image 이용  
즉, 클라이언트의 요청을 HAProxy가 받아 미리 지정된 Load Balancing 옵션에 따라 요청을 각 어플리케이션 서버로 전달  
- 현재는 요청을 순서대로 골고루 분배하는 round robin 방식 이용
- Docker Container들이 띄워진 후 http://localhost:8404/stats 주소로 접속하면 작동하는 서버들의 상태와 각 서버로 할당된 Request 숫자를 볼 수 있음

