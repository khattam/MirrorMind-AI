#!/usr/bin/env python3
"""
Simple script to view debate metrics from the command line
"""
import json
from services.metrics_service import MetricsService

def main():
    metrics_service = MetricsService()
    
    print("=" * 60)
    print("DEBATE METRICS SUMMARY")
    print("=" * 60)
    
    # Get summary stats
    summary = metrics_service.get_summary_stats()
    
    print(f"\n📊 Overall Statistics:")
    print(f"  Total Debates: {summary['total_debates']}")
    print(f"  Total Words: {summary['total_words']:,}")
    print(f"  Total Turns: {summary['total_turns']}")
    print(f"  Avg Debate Length: {summary['avg_debate_length']} turns")
    print(f"  Avg Words per Debate: {summary['avg_words_per_debate']:.0f}")
    print(f"  Most Common Winner: {summary['most_common_winner']}")
    print(f"  Most Used Agent: {summary['most_used_agent']}")
    
    print(f"\n🤖 Agent Usage:")
    for agent, count in sorted(summary['agent_usage'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {agent}: {count} debates")
    
    # Get all debates
    debates = metrics_service.get_all_metrics()
    
    if debates:
        print(f"\n📝 Recent Debates:")
        for debate in debates[-5:]:  # Show last 5
            print(f"\n  {debate['debate_id']}")
            print(f"    Title: {debate['dilemma_title']}")
            print(f"    Agents: {', '.join(debate['agents'])}")
            print(f"    Turns: {debate['total_turns']}, Words: {debate['total_words']}")
            print(f"    Winner: {debate['final_recommendation']} (confidence: {debate['confidence']}%)")
            print(f"    Most Verbose: {debate['most_verbose_agent']}")
    
    print("\n" + "=" * 60)
    print(f"Metrics stored in: {metrics_service.storage_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
