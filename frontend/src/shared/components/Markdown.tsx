import React from "react";

interface MarkdownProps {
  text: string;
}

export const Markdown = ({ text }: MarkdownProps) => {
  // Split content by code blocks first
  const parts = text.split(/(```[\s\S]*?```)/g);

  return (
    <div className="space-y-3 font-sans leading-relaxed text-xs md:text-sm">
      {parts.map((part, index) => {
        if (part.startsWith("```") && part.endsWith("```")) {
          // It's a code block
          const lines = part.slice(3, -3).trim().split("\n");
          const firstLine = lines[0] || "";
          const hasLanguage = !firstLine.includes(" ") && firstLine.length < 15 && firstLine.length > 0;
          const language = hasLanguage ? firstLine : "";
          const code = (hasLanguage ? lines.slice(1) : lines).join("\n");

          return (
            <div key={index} className="my-3 overflow-hidden rounded-xl border border-outline-variant/60 bg-background text-on-surface">
              {language && (
                <div className="flex justify-between items-center bg-surface-container/60 px-4 py-1.5 border-b border-outline-variant/40 text-[9px] font-bold uppercase tracking-wider text-on-surface-variant font-mono select-none">
                  <span>{language}</span>
                </div>
              )}
              <pre className="p-4 overflow-x-auto text-xs md:text-sm font-mono-code leading-relaxed bg-black/10">
                <code>{code}</code>
              </pre>
            </div>
          );
        }

        // Handle inline formatting: tables, lists, headings, paragraphs
        const lines = part.split("\n");
        let inList = false;
        let listItems: string[] = [];
        const renderedElements: React.ReactNode[] = [];

        const renderText = (txt: string) => {
          // Parse bold, inline code, and links/citations
          const tokens = txt.split(/(\*\*.*?\*\*|`.*?`|\[.*?\]\(.*?\))/g);
          return tokens.map((token, tIdx) => {
            if (token.startsWith("**") && token.endsWith("**")) {
              return <strong key={tIdx} className="font-extrabold text-primary">{token.slice(2, -2)}</strong>;
            }
            if (token.startsWith("`") && token.endsWith("`")) {
              return <code key={tIdx} className="bg-surface-container px-1.5 py-0.5 rounded font-mono-code text-[11px] md:text-xs text-primary">{token.slice(1, -1)}</code>;
            }
            if (token.startsWith("[") && token.includes("](")) {
              const labelEnd = token.indexOf("](");
              const label = token.slice(1, labelEnd);
              const url = token.slice(labelEnd + 2, -1);
              return (
                <a 
                  key={tIdx} 
                  href={url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-primary underline hover:text-primary/80 transition-colors font-bold uppercase tracking-wider text-[11px] md:text-xs"
                >
                  {label}
                </a>
              );
            }
            return token;
          });
        };

        const flushList = (key: number) => {
          if (listItems.length > 0) {
            renderedElements.push(
              <ul key={`ul-${key}`} className="list-disc pl-5 my-2 space-y-1">
                {listItems.map((item, lIdx) => (
                  <li key={lIdx} className="text-on-surface">{renderText(item)}</li>
                ))}
              </ul>
            );
            listItems = [];
            inList = false;
          }
        };

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i];
          const trimmed = line.trim();

          // Handle table rows
          if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
            flushList(i);
            // Parse table lines
            const cells = trimmed.split("|").slice(1, -1).map(c => c.trim());
            // Check if next lines are separator or rows
            let rows = [cells];
            let nextI = i + 1;
            while (nextI < lines.length && lines[nextI].trim().startsWith("|")) {
              const nextLine = lines[nextI].trim();
              if (!nextLine.includes("---")) {
                rows.push(nextLine.split("|").slice(1, -1).map(c => c.trim()));
              }
              nextI++;
            }
            i = nextI - 1;

            const headers = rows[0];
            const dataRows = rows.slice(1);

            renderedElements.push(
              <div key={`table-${i}`} className="my-4 overflow-x-auto rounded-xl border border-outline-variant/60 bg-background select-text">
                <table className="min-w-full divide-y divide-outline-variant/40 text-left text-xs md:text-sm">
                  <thead className="bg-surface-container/60 font-bold uppercase tracking-wider text-[10px] md:text-xs text-on-surface-variant">
                    <tr>
                      {headers.map((header, hIdx) => (
                        <th key={hIdx} className="px-4 py-3 font-semibold">{header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant/20 bg-background/50">
                    {dataRows.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-surface-container/20 transition-colors">
                        {row.map((cell, cIdx) => (
                          <td key={cIdx} className="px-4 py-3 font-medium">{renderText(cell)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
            continue;
          }

          // Handle Headings
          if (trimmed.startsWith("###")) {
            flushList(i);
            renderedElements.push(
              <h4 key={i} className="text-sm md:text-base font-extrabold text-primary uppercase tracking-wider mt-4 mb-2">
                {renderText(trimmed.slice(3).trim())}
              </h4>
            );
            continue;
          }
          if (trimmed.startsWith("##")) {
            flushList(i);
            renderedElements.push(
              <h3 key={i} className="text-base md:text-lg font-extrabold text-primary uppercase tracking-wider mt-5 mb-2">
                {renderText(trimmed.slice(2).trim())}
              </h3>
            );
            continue;
          }
          if (trimmed.startsWith("#")) {
            flushList(i);
            renderedElements.push(
              <h2 key={i} className="text-lg md:text-xl font-extrabold text-primary uppercase tracking-wider mt-6 mb-3">
                {renderText(trimmed.slice(1).trim())}
              </h2>
            );
            continue;
          }

          // Handle Lists
          if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
            inList = true;
            listItems.push(trimmed.slice(2));
            continue;
          }

          // Empty line
          if (trimmed === "") {
            flushList(i);
            continue;
          }

          // Plain text line
          if (inList) {
            listItems.push(trimmed);
          } else {
            renderedElements.push(
              <p key={i} className="my-1.5 leading-relaxed text-on-surface">
                {renderText(line)}
              </p>
            );
          }
        }

        // Flush any remaining list
        flushList(lines.length);

        return <React.Fragment key={index}>{renderedElements}</React.Fragment>;
      })}
    </div>
  );
};

export default Markdown;
