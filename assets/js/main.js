// main.js
    const backToTop = document.getElementById("backToTop");
    window.addEventListener("scroll", () => {
      if (window.scrollY > 300) {
        backToTop.style.display = "block";
      } else {
        backToTop.style.display = "none";
      }
    });
    backToTop.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

document.addEventListener("DOMContentLoaded", function () {
  // 1. 获取正文内的所有 H2 和 H3
  const headings = document.querySelectorAll("main h2");
  const tocList = document.querySelector(".sidebar-left ul");
  tocList.innerHTML = ""; // 清空原目录内容

  // 2. 动态为每个标题生成 id
  headings.forEach((heading, index) => {
    const id = "section-" + index;
    heading.id = id;

    // 3. 创建目录链接
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = "#" + id;
    a.textContent = heading.textContent;

    // 4. 根据 H2 / H3 缩进样式区分层级
    if (heading.tagName === "H3") {
      a.style.marginLeft = "15px";
      a.style.fontSize = "14px";
      a.style.color = "#555";
    }

    li.appendChild(a);
    tocList.appendChild(li);
  });

  // 5. 平滑滚动效果
  document.querySelectorAll('.sidebar-left a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        window.scrollTo({
          top: target.offsetTop - 100, // 顶部留出导航栏空间
          behavior: "smooth"
        });
      }
    });
  });
});
