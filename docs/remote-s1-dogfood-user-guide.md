# LLM Wiki Remote S1 — 아주 짧은 실사용 가이드

이 문서는 기능 설명서가 아니라 **실사용 dogfood 체크리스트**다. 평소에는 VS Code Agent와 자연스럽게 대화하고, 필요한 파일만 Project Memory에 기억시키면 된다.

## A PC를 Personal Wiki host로 쓰고, B PC에서 같이 쓰기

```text
A PC = Personal Wiki authority + 기존 Project Memory
B PC = client
```

### 0. 준비

- A와 B에 Remote S1 candidate VSIX를 설치한다.
- 둘 다 trusted single-folder Linux workspace에서 사용한다.
- **B -> A non-interactive SSH**가 동작해야 한다.
  - 예: B에서 `ssh <A-alias> true`
- B의 SSH 로그인 사용자는 A에서 Personal Wiki를 실행하는 Linux 사용자와 같아야 같은 authority catalog를 본다.
- **A -> A self-SSH는 필요 없다.**

## 1. A에서 현재 Project Memory 게시

A의 Doctor가 `Project memory: ON`이고 local store가 정상이라면:

1. 사이드바 **Personal Wiki · Not connected**
2. **Publish This Project Memory**
3. **This PC**
4. **Connected · read/write** 확인

이 단계가 A의 현재 로컬 Project Memory를 Personal Wiki의 새 opaque project identity로 게시한다.

## 2. B에서 A의 Project Memory 이어쓰기

B의 Doctor에서 다음 상태를 확인한다.

- Project memory: ON
- Local Project Memory contents: **EMPTY · READY TO USE EXISTING PERSONAL WIKI PROJECT**

그 다음:

1. 사이드바 **Personal Wiki · Not connected**
2. **Use Existing Personal Wiki Project Memory**
3. **SSH Host**
4. A로 접속되는 SSH alias 입력
5. A가 게시한 Project Memory 선택
6. **Connected · read/write** 확인

같은 Git repository/path/파일 내용이어도 자동 연결되지 않는다. 정확한 Project Memory는 사용자가 직접 선택한다.

## 3. 평소 사용

- 기억시키기: 파일 우클릭 -> **Remember in Project Memory**
- 질문하기: 평소처럼 VS Code Agent에게 질문
- 다른 PC에서 기억이 바뀐 뒤: **Refresh Personal Wiki**

## 4. 다른 프로젝트 기억 참고

**Manage Other Project Memories**에서 다른 프로젝트를 추가할 수 있다.

- 다른 프로젝트는 read-only
- 현재 workspace에서 사용하려면 **Allow Here** 별도 승인
- 다른 프로젝트에 쓰거나 전체 프로젝트를 자동 검색하지 않음

## 5. A와 연결이 끊기면

B는 **Offline · read only**가 된다.

- 마지막 verified memory는 읽을 수 있음
- 새 기억 저장/수정은 차단
- A 연결 복구 후 **Refresh Personal Wiki**

## Dogfood 원칙

아래 중 하나라도 막히면 가이드를 길게 쓰기 전에 UX 문제로 본다.

- 다음에 무엇을 눌러야 할지 모르겠다.
- A와 B 중 어디서 먼저 해야 하는지 모르겠다.
- Publish / Use Existing의 차이를 모르겠다.
- 현재 local memory가 attach 가능한 빈 상태인지 모르겠다.
- Offline에서 무엇이 가능한지 모르겠다.
- 내부 tool/CLI/저장 구조를 알아야 사용할 수 있다.

**목표:** 제품 UX가 좋아질수록 이 문서는 더 짧아져야 한다.
