#!/usr/bin/env node

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

function lintMarkdown() {
  try {
    // Run markdownlint-cli2 and capture output
    const output = execSync('pnpm exec markdownlint-cli2 "docs/**/*.md" --config .markdownlint.json', {
      encoding: 'utf8',
      stdio: 'pipe'
    });
    
    // If no output, return empty array
    if (!output.trim()) {
      console.log(JSON.stringify([]));
      return;
    }
    
    // Parse the output and convert to JSON
    const lines = output.trim().split('\n');
    const results = [];
    
    for (const line of lines) {
      // Skip summary lines
      if (line.includes('Summary:') || line.includes('Finding:') || line.includes('Linting:')) {
        continue;
      }
      
      // Parse error lines like: "docs/file.md:123 MD001/rule-name Description [Context: "..."]"
      const match = line.match(/^([^:]+):(\d+)(?::(\d+))?\s+([^\s]+)\s+(.+?)(?:\s+\[Context:\s*"([^"]*)"\])?$/);
      if (match) {
        const [, file, lineNum, colNum, rule, description, context] = match;
        results.push({
          file: file.trim(),
          line: parseInt(lineNum),
          column: colNum ? parseInt(colNum) : null,
          rule: rule,
          description: description.trim(),
          context: context || null
        });
      }
    }
    
    console.log(JSON.stringify(results, null, 2));
  } catch (error) {
    // If command fails, try to parse stderr for errors
    if (error.stderr) {
      const lines = error.stderr.trim().split('\n');
      const results = [];
      
      for (const line of lines) {
        const match = line.match(/^([^:]+):(\d+)(?::(\d+))?\s+([^\s]+)\s+(.+?)(?:\s+\[Context:\s*"([^"]*)"\])?$/);
        if (match) {
          const [, file, lineNum, colNum, rule, description, context] = match;
          results.push({
            file: file.trim(),
            line: parseInt(lineNum),
            column: colNum ? parseInt(colNum) : null,
            rule: rule,
            description: description.trim(),
            context: context || null
          });
        }
      }
      
      console.log(JSON.stringify(results, null, 2));
    } else {
      console.log(JSON.stringify([{ error: error.message }]));
    }
  }
}

lintMarkdown();