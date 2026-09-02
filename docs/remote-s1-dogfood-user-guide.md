# LLM Wiki Remote S1 — 아주 짧은 실사용 가이드

이 문서는 기능 설명서가 아니라 **실사용 dogfood용 체크리스트**다. 평소에는 VS Code Agent와 자연스럽게 대화하고, 필요한 파일만 Project Memory에 기억시키면 된다.

## 0. 준비

- GitHub의 `dogfood/releases/candidates/remote-s1/llm-wiki-dogfood-remote-s1-candidate.vsix`를 설치한다.
- 신뢰한 **single-folder Linux workspace**에서 사용한다. VS Code Remote-SSH를 쓰는 경우 LLM Wiki는 Linux workspace host에서 실행된다.
- LLM Wiki가 실행되는 Linux workspace host에서 Personal Wiki authority로 **non-interactive SSH**가 이미 동작해야 한다. 예: `ssh <alias> true`가 암호 입력 없이 성공.

> 이 SSH 준비 외에 일상 사용에서 터미널 명령이 필요하면 UX 개선 후보로 기록한다.

## 1. 처음 연결하기

1. LLM Wiki 사이드바에서 **Set Up Project Memory**를 누른다.
2. **Connect Personal Wiki**를 누른다.
3. 연결 방식을 고른다.
   - **Create New Project Memory**: 이 workspace의 새 독립 Project Memory를 만든다.
   - **Use Existing Project Memory**: 다른 PC/workspace에서 이미 쓰던 정확한 Project Memory를 이어 쓴다. 로컬 Project Memory가 비어 있을 때만 가능하다.
4. 기존 SSH alias 또는 `user@host`를 입력한다.
5. 상태가 **Connected · read/write**로 보이는지 확인한다.

같은 Git repository나 같은 파일 내용이어도 Project Memory가 자동으로 합쳐지지는 않는다. 같은 기억을 이어 쓰려면 반드시 **Use Existing Project Memory**로 명시적으로 선택한다.

## 2. 평소 사용

- 기억시키고 싶은 파일: Explorer/Editor 우클릭 → **Remember in Project Memory**.
- 이후에는 평소처럼 VS Code Agent에게 질문한다. LLM Wiki 내부 tool 이름을 외울 필요는 없다.
- 다른 PC에서 같은 Project Memory를 갱신했다면 **Refresh Personal Wiki**를 누른다.

예시:

- “전에 이 인증 구조를 왜 이렇게 정했지?”
- “이 기능 관련해서 예전에 저장한 근거가 있나?”
- “지난 결정과 지금 구현이 충돌하는 부분을 찾아줘.”

## 3. 다른 PC에서 같은 Project Memory 이어쓰기

새 PC/workspace에서:

1. **Set Up Project Memory**
2. **Connect Personal Wiki**
3. **Use Existing Project Memory**
4. 목록에서 이어 쓸 프로젝트를 직접 선택

연결 후 한쪽에서 기억을 추가하고, 다른 쪽에서 **Refresh Personal Wiki** 했을 때 그 기억이 보이면 된다.

## 4. 다른 프로젝트 기억 참고하기

**Manage Other Project Memories**에서 다른 프로젝트 하나를 선택해 추가할 수 있다.

- 추가한 다른 프로젝트는 **read-only**다.
- 등록만으로 접근 권한이 생기지 않는다. 현재 workspace에서 사용할 때 **Allow Here**를 별도로 승인한다.
- 다른 프로젝트에 쓰거나 모든 프로젝트를 자동으로 한꺼번에 검색하지 않는다.

## 5. 네트워크가 끊겼을 때

Personal Wiki authority에 연결할 수 없으면 상태는 **Offline · read only**가 된다.

- 마지막으로 검증된 로컬 복사본은 읽을 수 있다.
- 새 기억 저장/수정은 막힌다.
- 로컬 복사본은 오래됐을 수 있다.
- 연결이 돌아오면 **Refresh Personal Wiki**로 정상 상태를 복구한다.

## Dogfood 원칙

아래 중 하나라도 생기면 **가이드 설명을 늘리기 전에 UX 문제인지 먼저 본다**.

- 다음에 무엇을 눌러야 할지 모르겠다.
- 현재 Project Memory가 켜졌는지/연결됐는지 모르겠다.
- 저장이 성공했는지 모르겠다.
- `Create New`와 `Use Existing` 중 무엇을 골라야 할지 모르겠다.
- Offline인데 무엇이 가능하고 불가능한지 모르겠다.
- 다른 프로젝트 기억이 왜 안 보이는지 모르겠다.
- 내부 tool/CLI/저장 구조를 알아야만 사용할 수 있다.

**목표:** 이 문서는 앞으로 더 길어지는 것이 아니라, 제품 UX가 좋아지면서 오히려 더 짧아져야 한다.
