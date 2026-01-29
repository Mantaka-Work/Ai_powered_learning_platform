#include <stdio.h>

int main()
{
  int n;
  scanf("%d", &n);
  int adj[n][n];
  for (int i = 0; i < n; i++)
  {
    for (int j = 0; j < n; j++)
    {
      adj[i][j] = 0;
    }
  }
  int e;
  scanf("%d", &e);
  for (int i = 0; i < e; i++)
  {
    int u, v;
    scanf("%d%d", &u, &v);
    adj[u][v] = 1;
    adj[v][u] = 1;
  }

  int vis[n], col[n];
  for (int i = 0; i < n; i++)
  {
    vis[i] = 0;
    col[i] = 0;
  }
  int flag = 0;
  col[0] = 1;
  for (int i = 0; i < n; i++)
  {
    for (int j = 0; j < n; j++)
    {
      if (adj[i][j] == 1)
      {
        if (col[j] == col[i])
        {
          flag = 1;
        }
        else if (col[j] == 0)
        {
          col[j] = col[i] * -1;
        }
      }
    }
  }
  if (flag == 0)
  {
    printf("Possible");
  }
  else
  {
    printf("Impossible");
  }
}