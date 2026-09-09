# LLM Wiki Remote S1 — 아주 짧은 실사용 가이드

이 문서는 기능 설명서가 아니라 **실사용 dogfood용 체크리스트**다. 평소에는 VS Code Agent와 자연스럽게 대화하고, 필요한 파일만 Project Memory에 기억시키면 된다.

## 먼저 이해할 한 가지

**로컬 Project Memory와 Personal Wiki authority의 Project Memory는 자동으로 같은 것이 아니다.**

예를 들어:

```text
A PC
- 현재 workspace의 로컬 Project Memory
- Personal Wiki authority host 역할도 함

B PC
- A의 Personal Wiki authority에 SSH로 접속
```

B에서 **Use Existing Project Memory**를 쓰려면, 먼저 A의 로컬 Project Memory가 Personal Wiki authority에 **Create New Project Memory로 게시**되어 있어야 한다.

현재 S1 candidate의 제한상 A가 authority host 자신이라도 게시할 때 SSH transport를 사용한다. 따라서 지금은 **A -> A self-SSH도 non-interactive로 동작해야 한다.** 이 요구는 dogfood에서 발견된 UX 개선 대상이다.

## 0. 준비

- GitHub의 `dogfood/releases/candidates/remote-s1/llm-wiki-dogfood-remote-s1-candidate.vsix`를 설치한다.
- 신뢰한 **single-folder Linux workspace**에서 사용한다.
- 각 LLM Wiki workspace host에서 Personal Wiki authority로 **non-interactive SSH**가 동작해야 한다.
  - B -> A: `ssh <A-alias> true`
  - 현재 candidate에서 A가 authority이면서 A의 memory를 게시하려면 A -> A self-SSH도 필요.

> SSH 준비 외에 일상 사용에서 터미널 명령이 필요하면 UX 개선 후보로 기록한다.

## 1. A의 기존 Project Memory를 Personal Wiki에 게시

A에서 이미 **Project Memory On / Local memory store: initialized**라면:

1. LLM Wiki 사이드바의 **Personal Wiki · Not connected**를 누른다.
2. **Create New Project Memory**를 선택한다.
3. A 자신을 가리키는 non-interactive SSH alias를 입력한다.
4. 상태가 **Connected · read/write**가 되는지 확인한다.

이 단계가 끝나야 A의 Project Memory가 Personal Wiki authority catalog에 나타난다.

## 2. B에서 A의 Project Memory 이어쓰기

B의 로컬 Project Memory는 freshly initialized / empty 상태여야 한다.

1. LLM Wiki 사이드바의 **Personal Wiki · Not connected**를 누른다.
2. **Use Existing Project Memory**를 선택한다.
3. B -> A SSH alias를 입력한다.
4. 목록에서 A가 1단계에서 게시한 Project Memory를 직접 고른다.
5. **Connected · read/write** 상태를 확인한다.

같은 Git repository나 같은 파일 내용이어도 자동으로 같은 Project Memory가 되지 않는다.

## 3. 평소 사용

- 기억시키고 싶은 파일: Explorer/Editor 우클릭 -> **Remember in Project Memory**
- 이후에는 평소처럼 VS Code Agent에게 질문
- 다른 PC에서 같은 Project Memory가 갱신됐다면 -> **Refresh Personal Wiki**

## 4. 다른 프로젝트 기억 참고

**Manage Other Project Memories**에서 다른 프로젝트를 추가할 수 있다.

- 다른 프로젝트는 **read-only**
- 현재 workspace에서 사용하려면 **Allow Here** 별도 승인
- 다른 프로젝트에 쓰거나 모든 프로젝트를 자동 검색하지 않음

## 5. 네트워크가 끊기면

상태는 **Offline · read only**가 된다.

- 마지막 verified memory는 읽을 수 있음
- 새 기억 저장/수정은 막힘
- 연결 복구 후 **Refresh Personal Wiki**

## Dogfood 원칙

아래 중 하나라도 생기면 **가이드를 늘리기 전에 UX 문제인지 먼저 본다**.

- 어느 PC에서 무엇을 먼저 해야 하는지 모르겠다.
- "Create New"가 기존 로컬 memory를 Personal Wiki에 게시한다는 뜻인지 모르겠다.
- authority host에서 self-SSH가 왜 필요한지 모르겠다.
- 다음에 무엇을 눌러야 할지 모르겠다.
- Project Memory가 켜졌는지/연결됐는지 모르겠다.
- 저장이 성공했는지 모르겠다.
- Offline에서 무엇이 가능한지 모르겠다.
- 내부 tool/CLI/저장 구조를 알아야 사용할 수 있다.

**목표:** 제품 UX가 좋아질수록 이 문서는 더 짧아져야 한다.
