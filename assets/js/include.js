document.addEventListener("DOMContentLoaded", function () {
  const includes = document.querySelectorAll("[data-include]");
  includes.forEach(async (el) => {
    const file = el.getAttribute("data-include");
    try {
      const response = await fetch(file);
      if (!response.ok) throw new Error(`无法加载文件: ${file}`);
      const html = await response.text();
      el.innerHTML = html;
    } catch (error) {
      console.error("Include 加载错误:", error);
      el.innerHTML = `<p style="color:red;">无法加载模块：${file}</p>`;
    }
  });
});
