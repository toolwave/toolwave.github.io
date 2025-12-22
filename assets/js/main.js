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

// ====== 优惠码复制功能 ======
function copyPromoCode() {
  // 获取优惠码文本
  const promoCode = document.getElementById('promoCode').innerText;
  const copyBtn = document.querySelector('.copy-btn');
  const copyText = document.querySelector('.copy-text');

  // 复制到剪贴板
  navigator.clipboard.writeText(promoCode).then(function() {
    // 更新按钮状态
    copyBtn.classList.add('copied');
    copyText.innerText = '已复制';

    // 3秒后恢复按钮状态
    setTimeout(function() {
      copyBtn.classList.remove('copied');
      copyText.innerText = '复制';
    }, 1800);
  }).catch(function(err) {
    // 如果浏览器不支持clipboard API，使用传统方法
    const textarea = document.createElement('textarea');
    textarea.value = promoCode;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();

    try {
      document.execCommand('copy');
      copyBtn.classList.add('copied');
      copyText.innerText = '已复制';

      setTimeout(function() {
        copyBtn.classList.remove('copied');
        copyText.innerText = '复制';
      }, 3000);
    } catch (err) {
      alert('复制失败，请手动复制优惠码');
    }

    document.body.removeChild(textarea);
  });
}
