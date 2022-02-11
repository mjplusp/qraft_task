# qraft_task
QRAFT Technologies Sample Task

## Simple Backend Auth Server

#### 구현 및 테스트
python Django 웹 프레임워크 및 Python GraphQL 라이브러리인 Graphene을 이용해 구현  
1. Git Repository Clone 후 프로젝트 디렉토리에서 도커 이미지 생성
```
$ docker build -t qraft_users:latest ./
```
2. docker compose를 통해 컨테이너들 구동 (로드 밸런싱 테스트를 위해 같은 이미지의 컨테이너가 3개 구동됨)
```
$ docker compose up -d
```
3. http://localhost/graphql/ 주소로 접속하면 회원가입 및 로그인 API들을 테스트할 수 있음  
   
   **Container Running 상태에서 프록시 컨테이너가 세팅 완료 되기까지 약 2~30초 정도 소요될 수 있음**

   1. **회원가입**  
        **request body**
        ```graphql
        mutation {
        createUser(email: "test@gmail.com", password: "testpassword") {
            user {
            email
            password
            dateJoined
            }
        }
        }
        ```
        **response**
        ```graphql
        {
        "data": {
            "createUser": {
            "user": {
                "email": "test@gmail.com",
                "password": "pbkdf2_sha256$260000$uzRMRmBQ3kdP0dg3BwChhu$HSpWANxRgmraCWjGK4gCVdGai2rve362fd9iH7ucVqI="
                "dateJoined": "2022-02-11T04:22:55.155289+00:00"
            }
            }
        }
        }
        ```
        비밀번호는 sha256 방식을 통해 암호화 되어 저장됨. 본 Task에서는 Django에서 기본적으로 제공하는 비밀번호 암호화 기능을 이용했으나, 그 밖의 여러 해시 함수들(단방향)을 통해 입력된 암호를 해시 가능. 이 방법을 이용할 경우, 로그인 시에는 암호화된 비밀번호와 입력받은 raw 비밀번호가 같은지 검증하는 verify 함수를 통해 사용자 확인

   2. **로그인 (Json Web Token 반환)**  
        **request body**
        ```graphql
        mutation {
        login(email: "test@gmail.com", password: "testpassword") {
            token
            payload
        }
        }
        ```
        **response**
        ```graphql
        {
        "data": {
            "login": {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InRlc3RAZ21haWwuY29tIiwiZXhwIjoxNjQ0NTUzODI1LCJvcmlnSWF0IjoxNjQ0NTUzNTI1fQ.YQClmoMaqmalyunMvr1L-I5aQ1nn_6q1TpEorhnfCrU",
            "payload": {
                "email": "test@gmail.com",
                "exp": 1644553825,
                "origIat": 1644553525
            }
            }
        }
        }
        ```
      1. **기 존재하는 Web Token을 헤더에 포함한 상태로 로그인 시 이미 로그인 되었다는 텍스트 반환**  
        
          헤더 설정이 가능해야 하기에, Postman 등의 소프트웨어 이용해 Test  
          **Request URL:**  
          ```
          localhost/graphql/
          ```
          **Authorization Header 추가**
          ```
          Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InRlc3RAZ21haWwuY29tIiwiZXhwIjoxNjQ0NTUzODI1LCJvcmlnSWF0IjoxNjQ0NTUzNTI1fQ.YQClmoMaqmalyunMvr1L-I5aQ1nn_6q1TpEorhnfCrU
          ```
          **request body**  
          ```graphql
          mutation{
               login(email:"test@gmail.com" password:"testpassword"){
                    token
                    payload
               }
          }
          ```
          **response**
          ```graphql
          {
               "errors": [
                    {
                         "message": "이미 test@gmail.com로 로그인 하였습니다.(로그인 시도한 계정: test@gmail.com)",
                         "locations": [
                         {
                              "line": 2,
                              "column": 5
                         }
                         ],
                         "path": [
                         "login"
                         ]
                    }
               ],
               "data": {
                    "login": null
               }
          }
          ```
     * 관련 코드는 ./qraft/qraft_users/schema.py 내에서 확인 가능
  
**GraphQL**  
REST 방식에 비해 클라이언트가 원하는 데이터를 직접 선정해 서버에 요청할 수 있기에 REST 방식에서 발생하는 Overfetching / Underfetching 문제가 덜 발생할 것으로 생각되었고, Endpoint가 1개이기에 코드 수정이 용이했음

**Json Web Token**  
1. 로그인 시 서버는 사용자의 정보를 기반으로한 토큰을 발급. 이후 클라이언트가 서버에 요청을 할 때 마다 JWT를 포함하여 전달  
2. 서버는 요청을 받을때 마다, 해당 토큰이 유효한지 검증 후 작업 처리  
3. 서버는 사용자 세션을 유지할 필요 없이 토큰의 유효성만 검증하면 되기에 불필요한 서버 자원 낭비 막을 수 있음 (토큰기반 인증)  
4. 마찬가지로 토큰은 클라이언트가 가지고 있기에 매 번 로그인 정보를 확인할 필요가 없어 데이터베이스 부하 또한 줄일 수 있음  

## Logging

python에서 기본적으로 제공하는 logging 라이브러리 사용했음. Django를 통해 Format, Level, Handler (Console, File 등) 설정이 가능하고, 이를 통해 커스텀 Logger를 만들어 이용 가능. 현 Task에서는 Console과 File로 로그가 저장되도록 설정해 두었으며, File은 지정된 용량 초과 시 rolling되어 새로운 파일을 만들도록 설정해 두었음. 컨테이너 구현 후 graphql API 요청을 보내면 (유저 조회, 회원 가입 등) ./qraft/docker_data/logs/qraft_users.log 파일에 로그가 저장됨  

* 관련 설정은 ./qraft/qraft/settings.py 에서 LOGGING 항목 확인 가능

## Metric Monitoring

Docker 환경 내에서 구동되는 해당 서비스의 특성 상 Container 각각의 Metric 정보와 Host의 Metric 정보를 모두 수집할 필요가 있음. 이 Task에서는 오픈소스 모니터링 툴인 Prometheus를 이용하였음.    
1. 호스트, 컨테이너의 metric을 수집하는 Exporter 서버가 존재하고
2. Prometheus 서버는 Exporter Server의 EndPoint 주소로 접속해 Metric 데이터를 Scrapping 해옴   
3. Prometheus는 여러 Exporter로부터 수집한 Metric을 한데 모아 관리.  
4. 이후 Grafana와 같은 시각화 툴이 Prometheus 서버에 쿼리를 통해 데이터를 받아와 시각화
   1. 호스트와 컨테이너의 CPU 사용량, 메모리, Disk I/O, 네트워크 트래픽 등을 모니터링 할 수 있음

* 관련 설정은 ./prometheus/config/prometheus.yml 에서 확인 가능

#### 구현
본 Task에서는 윈도우 환경에 가상으로 리눅스 환경을 만들어 작업해서 많이 사용되는 컨테이너 및 호스트 Metrics Exporter인 cadvisor, node-exporter가 아닌, container-exporter를 이용했음. container_exporter 컨테이너가 Running 상태에서 http://localhost/metrics 에 접속 후 Export 되고 있는 Container Metric 정보를 확인할 수 있음

- 테스트 과정에서 컨테이너 running 시간이 지나다 보면 too many open files 에러가 발생하며 metrics exporter 서버가 응답없음 현상이 발생하는 것을 확인하였음. 현재까지는 container-exporter에 대한 이해가 부족하다고 생각됨

## Http TLS
기본 TLS 작동 메커니즘
1. 클라이언트에서 서버에 패킷을 전달하며 TCP 채널 오픈
2. 서버는 클라이언트에 인증서와 서버의 public key 전달
3. 클라이언트는 서버 인증서를 확인하고, public key를 이용해 대칭 키 생성 정보를 암호화해 서버로 전달
4. 서버는 private key를 이용해 이를 복호화 하고 세션 유효기간동안 사용할 수 있는 대칭 키 생성. 이를 이용해 암호화된 통신  

본 Task에서는 다음과 같이 구성  
1. 도커 환경 내부에서 운영되는 GraphQL API 서버 등은 외부에서 접속할 수 없도록 막아두고 (내부 컨테이너끼리는 통신 가능),  
2. 앞단의 프록시 서버(HAProxy)가 SSL 인증 정보 확인 및 암호화/복호화를 담당.  
3. 이후 프록시 서버는 도커 환경 내부의 API 서버로 http 프로토콜에 따라 통신

#### 구현
HAProxy에서 443 포트를 통한 https 통신에 발급한 인증서를 위치시켜두고 사용
* ssl 설정을 위해 git repo에 self-signed key 파일들을 업로드 해 두었음
* 위에 작성된 모든 테스트 주소들은 https 방식으로도 접근 및 이용이 가능
* Self-Signed 인증서이기 때문에 크롬 등의 클라이언트에서 등록되지 않은 인증서 경고 문구 발생 가능
* Authorization Header를 추가하기 위해 Postman 등을 이용할 경우, ssl 설정을 해제해 두고 테스트 해야 함
* 아래 코드는 openssl 소프트웨어를 통해 self-signed된 인증서 및 private key를 발급받기 위한 코드임

```
$ openssl genrsa -des3 -out server.key 2048 # 개인 키 생성 (2048bit, rsa des3 encoding)
$ openssl req -new -key server.key -out server.csr # 인증 요청서 생성
```
```
$ cp server.key server.key.origin # 개인 키 password 제거
$ openssl rsa -in server.key.origin -out server.key
```
```
$ openssl x509 -req -days 3650 -in server.csr -signkey server.key -out server.crt # 개인 키와 인증 요청서를 이용해 인증 키 생성
```

## Load Balancing / Health Check

1. **Load Balancing:** 클라이언트 수가 많아지며 서버에 부하가 걸리는데, 이를 효율적으로 분산하기 위해 사용
2. **Health Check:** 로드밸런싱 서비스를 제공하는 서버들의 통신 상태를 점검. 즉 서버가 제대로 서비스를 제공 가능한지 확인
   1. 단순히 서버들의 Network Interface가 up 상태인지만을 확인  
   2. 주기적으로 TCP Connection을 시도  
   3. 웹 애플리케이션이 잘 구동하고 있는지를 Test할 수도 있음.  
        - 웹 서버는 GET, POST 등 미리 지정된 Http Request를 보내고 서버가 성공 코드를 반환하는지 여부를 이용해 Health Check할 수도 있음

#### 구현
Health Check와 Load Balancing을 지원하는 **HAProxy** Docker Image 이용  
즉, 클라이언트의 요청을 HAProxy가 받아 미리 지정된 Load Balancing 옵션에 따라 요청을 각 어플리케이션 서버로 전달  
- 현재는 요청을 순서대로 골고루 분배하는 round robin 방식 이용
- Docker Container들이 띄워진 후 http://localhost/stats 주소로 접속하면 작동하는 서버들 (qraft 항목 내)의 상태와 각 서버로 할당된 Request 숫자를 볼 수 있음
- 관련 설정 값은 ./haproxy/haproxy.cfg 에서 확인 가능

