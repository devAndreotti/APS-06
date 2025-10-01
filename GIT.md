## 🎯 Situação inicial

* Você tem um projeto base na branch **`main`**.
* Você cria uma branch **`feature-ricardo`**.
* Outro dev cria uma branch **`feature-colega`**.

Assim cada um pode trabalhar isoladamente.

---

## 🔹 Passo a passo com exemplo

### 1. Criando as branches

```bash
git checkout main
git pull origin main

git checkout -b feature-ricardo   # sua branch
git push origin feature-ricardo

git checkout main
git checkout -b feature-colega    # branch do colega
git push origin feature-colega
```

---

### 2. Você adiciona uma função na sua branch

```bash
# dentro da feature-ricardo
git add .
git commit -m "Adiciona função de cálculo de desconto"
git push origin feature-ricardo
```

---

### 3. Mesclando na `main`

Quando terminar sua parte, você abre um **Pull Request** (PR) para `main`.
Depois que for revisado/aprovado:

```bash
git checkout main
git pull origin main
git merge feature-ricardo
git push origin main
```

Agora a **main já contém a função que você fez**.

---

### 4. E o colega que estava na branch antiga?

O colega ainda está em `feature-colega`, que foi criada **antes** do seu merge.
Ou seja, o código dele **não tem a sua função nova ainda**.
Para ele atualizar:

```bash
git checkout feature-colega
git pull origin main        # traz as mudanças da main (inclui sua função)
git merge main              # junta o que está na main com a branch dele
```

Se houver conflito, ele resolve. Agora ele continua o trabalho já com **a sua função integrada**.

---

## 🔎 Exemplo concreto

* **Main:** tem só a base do projeto.
* **Você (feature-ricardo):** adiciona a função `calcularDesconto()`.
* **Colega (feature-colega):** estava mexendo em um sistema de login.

👉 Depois do merge da sua branch:

* A `main` tem `calcularDesconto()`.
* O colega dá `git pull origin main` e mescla → agora a branch dele terá **login + desconto**.
* Quando ele terminar, vai abrir um PR com a branch dele, e o projeto principal (`main`) terá **base + desconto + login**.

---

⚡ Em resumo:

* Cada dev trabalha em branch própria.
* Ao terminar, faz merge na `main`.
* Quem ainda está em outra branch, precisa **atualizar a sua branch com a main** para não ficar para trás.